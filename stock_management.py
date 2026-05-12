import csv
import json
import datetime
import os
MEMBERS_FILENAME = "members.json"
FILENAME = "stock.csv"
PELLET_FILENAME = "pellet.csv"
PRIMERS_FILENAME = "primer.csv" 
LOG_FILENAME = "log.csv"

def load_data(filename):
    """CSVファイルから在庫データを読み込む"""
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                return [] # ヘッダーすらない空ファイルの場合は空リストを返す
            
            stock_list = []
            for row in reader:
                if len(row) < 10:
                    continue
                
                item = {
                    '細胞名': row[0],
                    'ストック数': int(row[1]) if row[1].isdigit() else 0, 
                    '保存日': row[2],
                    '保存者': row[3],
                    '種族': row[4],
                    '細胞種': row[5],
                    '継代数': row[6],    
                    '細胞数': row[7],    
                    '保存場所': row[8],
                    'コメント': row[9]
                }
                stock_list.append(item)
            return stock_list
    except FileNotFoundError:
        return []
    
def save(filename, stock_data):
    """在庫データをCSVファイルに保存する。"""
    # 新しい10列のヘッダーを定義
    header = ["細胞名", "ストック数",  "保存日", "保存者", "種族", "細胞種", "継代数", "細胞数", "保存場所","コメント"]
    
    with open(filename, "w", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        for item in stock_data:
            writer.writerow([
                item.get('細胞名', ''),
                item.get('ストック数', 0),     
                item.get('保存日', ''),
                item.get('保存者', ''),
                item.get('種族', ''),
                item.get('細胞種', ''),     
                item.get('継代数', ''),   
                item.get('細胞数', ''),   
                item.get('保存場所', ''),
                item.get('コメント', '') 
                                        ])

def load_members():
    try:
        with open(MEMBERS_FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルがない、または空の場合は初期リストを返す
        return ["（未登録）"]

def save_members(members):
    with open(MEMBERS_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=4)

def add_item(stock_data, new_item_dict):
    """GUIから受け取った新しいアイテム（辞書）をデータリストに追加する。"""
    stock_data.append(new_item_dict)
    print(f"データ追加: {new_item_dict.get('細胞名')}")

def delete_item(stock_data, item_to_delete):
    """GUIから受け取ったアイテム（辞書）をデータリストから削除する。"""
    if item_to_delete in stock_data:
        stock_data.remove(item_to_delete)
        print(f"データ削除: {item_to_delete.get('細胞名')}")
        return True
    return False

def use_stock_item(item_to_use, quantity):
    """指定されたアイテムのストック数を減らす。"""
    if item_to_use and 'ストック数' in item_to_use and item_to_use['ストック数'] >= quantity:
        item_to_use['ストック数'] -= quantity
        print(f"「{item_to_use.get('細胞名')}」を{quantity}個使用。")
        return True
    return False

def filter_items_by_keyword(stock_data, keyword):
    """キーワードに一致するアイテムのリストを返す。"""
    if not keyword:
        return stock_data # キーワードがなければ全件返す
    
    results = []
    keyword_lower = keyword.lower()
    for item in stock_data:
        if keyword_lower in item.get('細胞名', '').lower():
            results.append(item)
    return results

def log_action(action, item, operator, details=""):

    header = ["日時", "操作", "細胞名", "詳細", "操作者"]
    
    file_exists = os.path.exists(LOG_FILENAME)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_entry = [
        timestamp,
        action,
        item.get('細胞名', 'N/A'),
        details,
        operator 
    ]
    
    try:
        with open(LOG_FILENAME, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(log_entry)
        print(f"ログ記録: {log_entry}")
    except Exception as e:
        print(f"ログの記録に失敗しました: {e}")

def load_pellet_data(pellet):
    try:
        with open(pellet, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                return [] # ヘッダーすらない空ファイルの場合は空リストを返す
            
            pellet_list = []
            for row in reader:
                if len(row) < 7:
                    continue
                item = {
                    '細胞名': row[0],
                    'ストック数': int(row[1]) if row[1].isdigit() else 0, 
                    '保存日': row[2],
                    '保存者': row[3],
                    '細胞数': row[4],    
                    '保存場所': row[5],
                    'コメント': row[6]
                }
                pellet_list.append(item)
            return pellet_list
    except FileNotFoundError:
        return []

def save_pellet(pellet,pellet_data):
    header = ["細胞名", "ストック数",  "保存日", "保存者","細胞数", "保存場所","コメント"]

    with open(PELLET_FILENAME,"w",newline="",encoding = 'utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(header)

        for item in pellet_data:
            writer.writerow([
                item.get('細胞名', ''),
                item.get('ストック数', 0),     
                item.get('保存日', ''),
                item.get('保存者', ''), 
                item.get('細胞数', ''),   
                item.get('保存場所', ''),
                item.get('コメント', '') 
                                        ])

def load_primers():
    try:
        with open(PRIMERS_FILENAME, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except FileNotFoundError:
        return []

def save_primers(primers_data):
    # --- 【修正4】ヘッダーのTypo修正(Aplication->Application) ---
    if not primers_data:
        header = ["ID","Primer_Name", "Application","Animal","Sequence", "Length","Conc","保存場所","登録者","登録日","コメント"]
        with open(PRIMERS_FILENAME, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(header)
        return
        
    header = primers_data[0].keys()
    with open(PRIMERS_FILENAME, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(primers_data)

def add_primer_item(primers_data, new_primer_dict):
    """プライマーリストに新しいプライマーを追加する"""
    primers_data.append(new_primer_dict)
    print(f"プライマー追加: {new_primer_dict.get('プライマー名')}")

def delete_primer_item(primers_data, primer_to_delete):
    """プライマーリストから指定されたプライマーを削除する"""
    if primer_to_delete in primers_data:
        primers_data.remove(primer_to_delete)
        print(f"プライマー削除: {primer_to_delete.get('プライマー名')}")
        return True
    return False