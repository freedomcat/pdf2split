#!/usr/bin/env python3
import os
import re
import csv
import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from io import BytesIO

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2が見つかりません: pip install PyPDF2")
    exit(1)

# ログ設定
def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """ログ設定を初期化"""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(levelname)s: %(message)s'
    
    handlers = []
    
    # コンソール出力
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    handlers.append(console_handler)
    
    # ファイル出力（指定された場合）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(format_str))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format=format_str
    )

logger = logging.getLogger(__name__)

MODEL_LIMITS = {
    "chatgpt": 20 * 1024 * 1024,      # 20MB
    "notebooklm": 200 * 1024 * 1024   # 200MB
}

class PDFSplitterError(Exception):
    """PDF分割処理の例外"""
    pass

def validate_inputs(pdf_path: str, csv_path: Optional[str] = None) -> None:
    """入力ファイルの検証"""
    if not Path(pdf_path).exists():
        raise PDFSplitterError(f"PDFファイルが見つかりません: {pdf_path}")
    
    if csv_path and not Path(csv_path).exists():
        raise PDFSplitterError(f"CSVファイルが見つかりません: {csv_path}")

def safe_filename(title: str) -> str:
    """ファイル名として安全な文字列に変換"""
    # 不正文字を置換し、長すぎるファイル名を制限
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", title)
    return safe_name[:200]  # ファイル名長制限

def estimate_pdf_size(writer: PdfWriter) -> int:
    """PDFのサイズを推定（正確ではないが高速）"""
    # 簡易推定：ページ数 × 平均ページサイズ
    # より正確にはbufferに書き出す必要があるが、パフォーマンスとのトレードオフ
    page_count = len(writer.pages)
    if page_count == 0:
        return 0
    
    # 実際のサイズチェックは最後のページ追加時のみ実行
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.tell()

def save_pdf(writer: PdfWriter, base_name: str, part: int, 
             start_page: int, end_page: int) -> str:
    """PDFファイルを保存"""
    if len(writer.pages) == 0:
        logger.warning("空のPDFファイルをスキップします")
        return ""
    
    output_file = f"{base_name}_part{part:02d}.pdf"
    try:
        with open(output_file, "wb") as f:
            writer.write(f)
        logger.info(f"✅ {output_file} (ページ {start_page+1}–{end_page+1})")
        return output_file
    except Exception as e:
        raise PDFSplitterError(f"ファイル保存エラー: {e}")

def load_split_points(csv_path: str) -> List[Tuple[str, int]]:
    """CSVファイルから分割ポイントを読み込み"""
    split_points = []
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required_columns = {"title", "page"}
            
            if not required_columns.issubset(reader.fieldnames or []):
                raise PDFSplitterError(
                    f"CSVに必要な列がありません: {required_columns}"
                )
            
            for row_num, row in enumerate(reader, 1):
                try:
                    title = row["title"].strip()
                    page = int(row["page"]) - 1  # 1ベースから0ベースに変換
                    if page < 0:
                        raise ValueError("ページ番号は1以上である必要があります")
                    split_points.append((title, page))
                except (ValueError, KeyError) as e:
                    logger.warning(f"CSVの{row_num}行目をスキップ: {e}")
        
        if not split_points:
            raise PDFSplitterError("有効な分割ポイントがありません")
            
        split_points.sort(key=lambda x: x[1])
        return split_points
        
    except Exception as e:
        raise PDFSplitterError(f"CSV読み込みエラー: {e}")

def split_with_csv(pdf_path: str, csv_path: str, max_size: int) -> None:
    """CSVファイルに基づいてPDFを分割"""
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            raise PDFSplitterError("PDFにページがありません")
            
        split_points = load_split_points(csv_path)
        
        # ページ番号の妥当性チェック
        for title, page in split_points:
            if page >= total_pages:
                logger.warning(f"セクション '{title}' のページ番号 {page+1} が総ページ数 {total_pages} を超えています")
        
        for i, (title, start_page) in enumerate(split_points):
            if start_page >= total_pages:
                continue
                
            end_page = min(
                split_points[i+1][1] if i+1 < len(split_points) else total_pages,
                total_pages
            )
            
            if start_page >= end_page:
                continue
            
            split_section_by_size(reader, title, start_page, end_page, max_size)
            
    except Exception as e:
        if isinstance(e, PDFSplitterError):
            raise
        raise PDFSplitterError(f"PDF処理エラー: {e}")

def split_section_by_size(reader: PdfReader, title: str, start_page: int, 
                         end_page: int, max_size: int) -> None:
    """指定されたページ範囲をサイズ制限に基づいて分割"""
    safe_title = safe_filename(title)
    writer = PdfWriter()
    part = 1
    chunk_start = start_page
    
    for page_num in range(start_page, end_page):
        writer.add_page(reader.pages[page_num])
        
        # 定期的にサイズチェック（毎5ページまたは最後のページ）
        if (page_num - start_page + 1) % 5 == 0 or page_num == end_page - 1:
            current_size = estimate_pdf_size(writer)
            
            if current_size > max_size and len(writer.pages) > 1:
                # 最後のページを除いて保存
                temp_writer = PdfWriter()
                for page in writer.pages[:-1]:
                    temp_writer.add_page(page)
                
                save_pdf(temp_writer, safe_title, part, chunk_start, page_num - 1)
                part += 1
                
                # 新しいチャンクを開始
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                chunk_start = page_num
    
    # 残りのページを保存
    if len(writer.pages) > 0:
        save_pdf(writer, safe_title, part, chunk_start, end_page - 1)

def split_by_size(pdf_path: str, max_size: int) -> None:
    """サイズ制限に基づいてPDFを分割"""
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            raise PDFSplitterError("PDFにページがありません")
        
        base_name = Path(pdf_path).stem
        writer = PdfWriter()
        part = 1
        chunk_start = 0
        
        for page_num in range(total_pages):
            writer.add_page(reader.pages[page_num])
            
            # 定期的にサイズチェック
            if (page_num + 1) % 5 == 0 or page_num == total_pages - 1:
                current_size = estimate_pdf_size(writer)
                
                if current_size > max_size and len(writer.pages) > 1:
                    # 最後のページを除いて保存
                    temp_writer = PdfWriter()
                    for page in writer.pages[:-1]:
                        temp_writer.add_page(page)
                    
                    save_pdf(temp_writer, base_name, part, chunk_start, page_num - 1)
                    part += 1
                    
                    # 新しいチャンクを開始
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num])
                    chunk_start = page_num
        
        # 残りのページを保存
        if len(writer.pages) > 0:
            save_pdf(writer, base_name, part, chunk_start, total_pages - 1)
            
    except Exception as e:
        if isinstance(e, PDFSplitterError):
            raise
        raise PDFSplitterError(f"PDF処理エラー: {e}")

def main(pdf_file: str, csv_file: Optional[str], target: str) -> None:
    """メイン処理"""
    try:
        # 入力検証
        validate_inputs(pdf_file, csv_file)
        
        max_size = MODEL_LIMITS[target]
        logger.info(f"最大ファイルサイズ: {max_size / (1024*1024):.1f}MB ({target})")
        
        # CSVファイルが指定されていない場合のデフォルト検索
        if not csv_file:
            default_csv = Path(pdf_file).parent / "index.csv"
            if default_csv.exists():
                csv_file = str(default_csv)
                logger.info(f"デフォルトCSVファイルを使用: {csv_file}")
        
        # 分割実行
        if csv_file and Path(csv_file).exists():
            logger.info("CSVベースの分割を実行")
            split_with_csv(pdf_file, csv_file, max_size)
        else:
            logger.info("サイズベースの分割を実行")
            split_by_size(pdf_file, max_size)
            
        logger.info("分割完了")
        
    except PDFSplitterError as e:
        logger.error(f"処理エラー: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PDF分割ツール - CSVインデックスまたはサイズ制限で分割",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s -pdf document.pdf --target chatgpt
  %(prog)s -pdf document.pdf -csv index.csv --target notebooklm
  
CSVファイル形式:
  title,page
  Chapter 1,1
  Chapter 2,15
        """
    )
    
    parser.add_argument("-pdf", "--pdf_file", required=True,
                        help="入力PDFファイル")
    parser.add_argument("-csv", "--csv_file", default=None,
                        help="CSVファイル（オプション）")
    parser.add_argument("--target", choices=MODEL_LIMITS.keys(), default="chatgpt",
                        help="対象プラットフォーム (デフォルト: chatgpt)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="詳細ログを表示")
    parser.add_argument("--log-file", default=None,
                        help="ログファイルのパス（指定しない場合はコンソールのみ）")
    
    args = parser.parse_args()
    
    # ログ設定を初期化
    setup_logging(args.verbose, args.log_file)
    
    main(args.pdf_file, args.csv_file, args.target)
