import sys 
import csv
import platform # 追加: OS判定用
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QAbstractItemView,
    QListWidget, QPushButton, QLabel, QLineEdit,QSizePolicy,
    QTableWidgetItem, QMessageBox, QHeaderView,QStyledItemDelegate,
    QDialog, QDialogButtonBox, QFormLayout,QFrame,
    QComboBox, QSpinBox, QDateEdit
)
from PyQt5.QtGui import (QFont, QColor)
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt
import stock_management as sm
import os

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    if "Contents/MacOS" in application_path:
        application_path = os.path.abspath(os.path.join(application_path, "../../.."))
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

sm.FILENAME = os.path.join(application_path, "stock.csv")
sm.PELLET_FILENAME = os.path.join(application_path, "pellet.csv")
sm.PRIMERS_FILENAME = os.path.join(application_path, "primer.csv") 
sm.LOG_FILENAME = os.path.join(application_path, "log.csv")
sm.MEMBERS_FILENAME = os.path.join(application_path, "members.json")

# ホーム画面のクラス
class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("研究室在庫管理システム - ホーム")
        self.setGeometry(200, 100, 1400, 900)
        self.cell_manager_window = None
        self.primer_manager_window = None 

        #メインボタン用のスタイル
        main_button_style = """
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                padding: 25px;
                margin: 15px;
                color: #333;
                border: 1px solid #aaa;
                border-radius: 12px; /* 角の丸み */
                /* グラデーション */
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #fdfdfd, stop: 1 #e1e1e1);
            }
            /* マウスが乗った時の色 (ホバーエフェクト) */
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #e8e8e8, stop: 1 #d1d1d1);
            }
            /* クリックした時の色 */
            QPushButton:pressed {
                background-color: #c5c5c5;
                border: 1px solid #888;
            }
        """
        
        # 右下のボタン用のスタイル
        sub_button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #aaa;
                border-radius: 10px; /* 角の丸み */
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """


        main_container_layout = QVBoxLayout()
        center_buttons_layout = QVBoxLayout()
        center_buttons_layout.addStretch(1)
        
        self.stock_button = QPushButton("細胞の凍結ストック管理")
        self.stock_button.setStyleSheet(main_button_style)
        self.stock_button.clicked.connect(self.open_cell_manager_window)

        self.pellet_button = QPushButton("セルペレット管理 ")
        self.pellet_button.setStyleSheet(main_button_style)
        self.pellet_button.clicked.connect(self.open_cell_pellet_manager_window)

        self.log_button = QPushButton("操作ログ閲覧")
        self.log_button.setStyleSheet(main_button_style)
        self.log_button.clicked.connect(self.open_log_viewer)

        self.primer_button = QPushButton("プライマー管理")
        self.primer_button.setStyleSheet(main_button_style)
        self.primer_button.clicked.connect(self.open_primer_manager)

        center_buttons_layout.addWidget(self.stock_button)
        center_buttons_layout.addWidget(self.pellet_button)
        center_buttons_layout.addWidget(self.primer_button)
        center_buttons_layout.addWidget(self.log_button)
        center_buttons_layout.addStretch(1)

        corner_layout = QHBoxLayout()
        corner_layout.addStretch(1)

        self.member_button = QPushButton("メンバー\n登録")
        self.member_button.setStyleSheet(sub_button_style)
        self.member_button.clicked.connect(self.open_member_dialog)
        self.member_button.setFixedSize(100, 100)
        
        corner_layout.addWidget(self.member_button)

        main_container_layout.addLayout(center_buttons_layout)
        main_container_layout.addStretch(1)
        main_container_layout.addLayout(corner_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_container_layout)
        self.setCentralWidget(central_widget)

    def open_cell_manager_window(self):
        self.cell_manager_window = CellManagerWindow(self)
        self.cell_manager_window.show()
        self.hide()

    def open_cell_pellet_manager_window(self):
        self.cell_pellet_window = CellpelletWindow(self)
        self.cell_pellet_window.show()
        self.hide()

    def open_primer_manager(self):
        self.primer_manager_window = PrimerManagerWindow(self)
        self.primer_manager_window.show()
        self.hide()

    def open_member_dialog(self):
        dialog = MemberDialog(self)
        dialog.exec()

    def open_log_viewer(self):
        dialog = LogViewerDialog(self)
        dialog.exec()

# 凍結ストックの詳細画面のクラス
class CellManagerWindow(QMainWindow):
    def __init__(self, home_window):
        super().__init__()
        self.home_window = home_window
        self.setWindowTitle("細胞凍結ストック管理")
        self.setGeometry(100, 100, 1600, 900)
        self.stock_data = sm.load_data(sm.FILENAME)
        self.currently_displayed_data = self.stock_data
        self.member_list = sm.load_members()
        self.current_keyword = ""

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["細胞名", "ストック数", "保存日", "保存者", "種族", "細胞種", "継代数", "細胞数", "保存場所", "コメント"])
        self.table.setStyleSheet("""
            QTableWidget { font-size: 11pt; gridline-color: #D0D0D0; }
            QHeaderView::section {
                background-color: #F0F0F0; font-weight: bold; font-size: 10pt;
                padding: 4px; border: 1px solid #D0D0D0;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.table.setColumnWidth(0, 220)  # 細胞名
        self.table.setColumnWidth(1, 70)   # ストック数
        self.table.setColumnWidth(2, 100)  # 保存日
        self.table.setColumnWidth(3, 100)  # 保存者
        self.table.setColumnWidth(4, 70)   # 種族
        self.table.setColumnWidth(5, 100)  # 細胞種
        self.table.setColumnWidth(6, 60)   # 継代数
        self.table.setColumnWidth(7, 100)  # 細胞数
        self.table.setColumnWidth(8, 250)  # 保存場所
        self.table.setColumnWidth(9, 250)  # コメント
        
        # 追加: Mac等でウィンドウ幅を広げた時に最後の列が伸びるようにする
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
       
        menu_layout = QHBoxLayout()
        
        search_button = QPushButton("検索")
        use_button = QPushButton("使用")
        add_button = QPushButton("追加")
        delete_button = QPushButton("削除")
        back_button = QPushButton("ホームに戻る")

        menu_layout.addWidget(search_button)
        menu_layout.addWidget(use_button)
        menu_layout.addWidget(add_button)
        menu_layout.addWidget(delete_button)
        menu_layout.addWidget(back_button)
        
        main_layout.addWidget(self.table)
        main_layout.addLayout(menu_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        search_button.clicked.connect(self.search_item)
        use_button.clicked.connect(self.use_item)
        add_button.clicked.connect(self.add_item)
        delete_button.clicked.connect(self.delete_item)
        back_button.clicked.connect(self.go_home)
        
        self.update_table()

    def update_table(self, data_to_display=None):
        self.currently_displayed_data = data_to_display if data_to_display is not None else self.stock_data
        self.table.setRowCount(len(self.currently_displayed_data))
        for i, item in enumerate(self.currently_displayed_data):
            self.table.setItem(i, 0, QTableWidgetItem(item.get('細胞名', '')))
            self.table.setItem(i, 1, QTableWidgetItem(str(item.get('ストック数', 0))))
            self.table.setItem(i, 2, QTableWidgetItem(item.get('保存日', "")))
            self.table.setItem(i, 3, QTableWidgetItem(item.get('保存者', '')))
            self.table.setItem(i, 4, QTableWidgetItem(item.get('種族', '')))
            self.table.setItem(i, 5, QTableWidgetItem(item.get('細胞種', ''))) 
            self.table.setItem(i, 6, QTableWidgetItem(str(item.get('継代数', 0))))
            self.table.setItem(i, 7, QTableWidgetItem(str(item.get('細胞数', 0))))
            self.table.setItem(i, 8, QTableWidgetItem(item.get('保存場所', '')))
            self.table.setItem(i, 9, QTableWidgetItem(item.get("コメント", "")))

    def search_item(self):
        dialog = SearchDialog(self)
        if dialog.exec():
            keyword = dialog.get_keyword()
            self.current_keyword = keyword
            if not keyword:
                self.update_table()
                return
            filtered_list = sm.filter_items_by_keyword(self.stock_data, keyword)
            self.update_table(data_to_display=filtered_list)

    def add_item(self):
        all_locations = [item.get('保存場所', '') for item in self.stock_data]
        dialog = AddDialog(self.member_list, all_locations, self)

        if dialog.exec():
            try:
            # 入力データを取得
                new_data = dialog.get_data()
                if not new_data["細胞名"] or new_data["ストック数"] <= 0:
                    QMessageBox.warning(self, "入力エラー", "細胞名と正しいストック数を入力してください。")
                    return
            
                #データをリストに追加
                sm.add_item(self.stock_data, new_data)
            
                #「保存者」の名前のログ記録
                saver_name = new_data.get('保存者', 'N/A')
                details = f"{new_data['ストック数']}個登録"
                sm.log_action("追加", new_data, saver_name, details)
            
                self.refresh_display()

            except ValueError:
                 QMessageBox.critical(self, "入力エラー", "細胞数の形式が正しくありません。\n例: 1.5e6 や 1500000 のように入力してください。")

    def use_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "選択エラー", "使用するアイテムをテーブルで選択してください。")
            return
    
        if selected_row >= len(self.currently_displayed_data):
            QMessageBox.critical(self, "データ不整合エラー", "表示とデータが一致しませんでした。")
            self.update_table()
            return
    
        item_to_use = self.currently_displayed_data[selected_row]
        locations_str = item_to_use.get("保存場所", "")

        if not locations_str:
            QMessageBox.warning(self, "エラー", "この在庫には保存場所が登録されていません。")
            return

        dialog = UseLocationDialog(locations_str, self)
        if dialog.exec():
            locations_to_use_simple = dialog.get_used_locations() 

            if not locations_to_use_simple:
                return # 何も選択されなかった場合は何もしない
            
            user_dialog = SelectUserDialog(self.member_list, self)
            if user_dialog.exec():
                
                # 3. 選択された使用者名を取得
                user_name = user_dialog.get_selected_user()
                all_locations = [loc.strip() for loc in locations_str.split(',')]
                
                # 使用する場所の完全な名前リストを作成
                base_prefix = "-".join(all_locations[0].split('-')[:-1]) if all_locations else ""
                full_locations_to_use = [f"{base_prefix}-{pos}" for pos in locations_to_use_simple]
                
                # 残った場所のリストを作成
                remaining_locations = [loc for loc in all_locations if loc not in full_locations_to_use]
                item_to_use["保存場所"] = ", ".join(remaining_locations)
                item_to_use["ストック数"] = len(remaining_locations)
                
                 # ログを記録
                details = f"{len(full_locations_to_use)}個使用。場所: {', '.join(full_locations_to_use)}"
                sm.log_action("使用", item_to_use, user_name, details) 
                
                # テーブルを更新
                self.refresh_display()

    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
           QMessageBox.warning(self, "選択エラー", "削除する行をテーブルで選択してください。")
           return

        if selected_row >= len(self.currently_displayed_data):
           QMessageBox.critical(self, "データ不整合エラー", "表示データが不正です。")
           self.update_table()
           return
        
        # 表示されているリストからアイテムを取得
        item_to_delete_display = self.currently_displayed_data[selected_row]

       # マスターデータ(self.stock_data)から、表示アイテムと完全に一致するものを探す
        item_to_delete_master = None
        for item in self.stock_data:
            if item == item_to_delete_display:
                item_to_delete_master = item
                break

        if item_to_delete_master is None:
            QMessageBox.critical(self, "エラー", "データから削除対象が見つかりませんでした。")
            return

        # 1. 最初に削除の意思を確認する
        reply = QMessageBox.question(self, '確認', f"「{item_to_delete_master.get('細胞名')}」を削除しますか？",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.No)
    
        # 「Yes」が押された場合のみ、次の処理へ進む
        if reply == QMessageBox.StandardButton.Yes:
            # 2. 次に「誰が」操作したかを選択するダイアログを開く
            user_dialog = SelectUserDialog(self.member_list, self)
            if user_dialog.exec():
                # 3. 選択された使用者名を取得する
                user_name = user_dialog.get_selected_user()

                # 4. 取得した使用者名を含めてログを記録し、データを削除する
                sm.log_action("削除", item_to_delete_master, user_name)
                sm.delete_item(self.stock_data, item_to_delete_master)
                self.refresh_display()

    def refresh_display(self):
        """現在の検索状態を維持したまま、表示を更新する"""
        if self.current_keyword:
            filtered_list = sm.filter_items_by_keyword(self.stock_data, self.current_keyword)
            self.update_table(data_to_display=filtered_list)
        else:
            self.update_table()

    def go_home(self):
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '確認', "データを保存してホーム画面に戻りますか？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
    
        if reply == QMessageBox.StandardButton.Yes:
            sm.save(sm.FILENAME, self.stock_data)
            self.home_window.show()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            self.home_window.show()
            event.accept()
        else:
            event.ignore()

# セルペレットの詳細画面のクラス
class CellpelletWindow(QMainWindow):
    def __init__(self, home_window):
        super().__init__()
        self.home_window = home_window
        self.setWindowTitle("セルペレット管理")
        self.setGeometry(150, 150, 1400, 800)
        self.pellet_data = sm.load_pellet_data(sm.PELLET_FILENAME)
        self.member_list = sm.load_members()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["細胞名", "ストック数", "保存日", "保存者","細胞数", "保存場所", "コメント"])
        self.table.setStyleSheet("""
            QTableWidget { font-size: 11pt; gridline-color: #D0D0D0; }
            QHeaderView::section {
                background-color: #F0F0F0; font-weight: bold; font-size: 10pt;
                padding: 4px; border: 1px solid #D0D0D0;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.table.setColumnWidth(0, 220)  # 細胞名
        self.table.setColumnWidth(1, 70)   # ストック数
        self.table.setColumnWidth(2, 120)  # 保存日
        self.table.setColumnWidth(3, 130)  # 保存者
        self.table.setColumnWidth(4, 150)  # 細胞数
        self.table.setColumnWidth(5, 120)  # 保存場所
        self.table.setColumnWidth(6, 250)  # コメント

        # 追加: Mac等でウィンドウ幅を広げた時に最後の列が伸びるようにする
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
       
        menu_layout = QHBoxLayout()
        
        use_button = QPushButton("使用")
        add_button = QPushButton("追加")
        delete_button = QPushButton("削除")
        back_button = QPushButton("ホームに戻る")

        menu_layout.addWidget(use_button)
        menu_layout.addWidget(add_button)
        menu_layout.addWidget(delete_button)
        menu_layout.addWidget(back_button)
        
        main_layout.addWidget(self.table)
        main_layout.addLayout(menu_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        use_button.clicked.connect(self.use_item)
        add_button.clicked.connect(self.add_item)
        delete_button.clicked.connect(self.delete_item)
        back_button.clicked.connect(self.go_home)
        
        self.update_table()

    def update_table(self, data_to_display=None):
        self.currently_displayed_data = data_to_display if data_to_display is not None else self.pellet_data
        self.table.setRowCount(len(self.currently_displayed_data))
        for i, item in enumerate(self.currently_displayed_data):
            self.table.setItem(i, 0, QTableWidgetItem(item.get('細胞名', '')))
            self.table.setItem(i, 1, QTableWidgetItem(str(item.get('ストック数', 0))))
            self.table.setItem(i, 2, QTableWidgetItem(item.get('保存日', "")))
            self.table.setItem(i, 3, QTableWidgetItem(item.get('保存者', '')))
            self.table.setItem(i, 4, QTableWidgetItem(str(item.get('細胞数', 0))))
            self.table.setItem(i, 5, QTableWidgetItem(item.get('保存場所', '')))
            self.table.setItem(i, 6, QTableWidgetItem(item.get("コメント", "")))

    def add_item(self):
        dialog = AddPelletDialog(self.member_list, self)
        if dialog.exec():
            new_data = dialog.get_data()
            sm.add_item(self.pellet_data, new_data) 
            saver_name = new_data.get('保存者', 'N/A')
            details = f"{new_data.get('ストック数', 0)}個登録"
            sm.log_action("ペレット追加", new_data, saver_name, details)

            self.update_table()

    def use_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "選択エラー", "使用するペレットを選択してください。")
            return
        
        item_to_use = self.pellet_data[selected_row]
        
        dialog = UseDialog(item_to_use.get('細胞名'), int(item_to_use.get('ストック数', 0)), self)
        if dialog.exec():
            quantity = dialog.get_quantity()
            user_dialog = SelectUserDialog(self.member_list, self)
            if user_dialog.exec():
                user_name = user_dialog.get_selected_user()
                
                item_to_use['ストック数'] = int(item_to_use.get('ストック数', 0)) - quantity
                details = f"{quantity}個使用"
                sm.log_action("ペレット使用", item_to_use, user_name, details)
                
                self.update_table()

    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "選択エラー", "削除するペレットを選択してください。")
            return
        
        item_to_delete = self.pellet_data[selected_row]
        reply = QMessageBox.question(self, '確認', f"「{item_to_delete.get('細胞名')}」のペレットを削除しますか？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            user_dialog = SelectUserDialog(self.member_list, self)
            if user_dialog.exec():
                user_name = user_dialog.get_selected_user()
                sm.delete_item(self.pellet_data, item_to_delete) 
                sm.log_action("ペレット削除", item_to_delete, user_name, "")
                self.update_table()

    def go_home(self):
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '確認', "変更を保存してホーム画面に戻りますか？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
    
        if reply == QMessageBox.StandardButton.Yes:
            sm.save_pellet(sm.PELLET_FILENAME, self.pellet_data)
            self.home_window.show()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            self.home_window.show()
            event.accept()
        else:
            event.ignore()

# セルペレット追加用のダイアログクラス
class AddPelletDialog(QDialog):
    def __init__(self, member_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新規ペレット追加")

        form_layout = QFormLayout(self)
        
        #入力ウィジェットの作成 
        self.name_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setRange(1, 999)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        
        self.saver_input = QComboBox()
        if member_list:
            self.saver_input.addItems(member_list)
        
        self.cell_count_input = QLineEdit()
        self.cell_count_input.setPlaceholderText("例: 1.5*10^6 または unknown")
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("例: Pellet Box 1")

        self.comment_input = QLineEdit()

        # レイアウトへの追加
        form_layout.addRow("細胞名:", self.name_input)
        form_layout.addRow("ストック数:", self.stock_input)
        form_layout.addRow("保存日:", self.date_input)
        form_layout.addRow("保存者:", self.saver_input)
        form_layout.addRow("細胞数:", self.cell_count_input)
        form_layout.addRow("保存場所:", self.location_input)
        form_layout.addRow("コメント:", self.comment_input)
        
        # ボタン 
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        form_layout.addWidget(button_box)

    def get_data(self):
        """入力されたデータを辞書として返す"""
        return {
            '細胞名': self.name_input.text(),
            'ストック数': self.stock_input.value(),
            '保存日': self.date_input.date().toString("yyyy-MM-dd"),
            '保存者': self.saver_input.currentText(),
            '細胞数': self.cell_count_input.text(),
            '保存場所': self.location_input.text(),
            'コメント': self.comment_input.text()
        }

# セルペレットの在庫使用数を入力するためのダイアログクラス
class UseDialog(QDialog):
    def __init__(self, item_name, max_stock, parent=None):
        super().__init__(parent)
        self.setWindowTitle("在庫使用")
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel(f"「{item_name}」をいくつ使用しますか？")
        layout.addWidget(info_label)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, max_stock) 
        layout.addWidget(self.quantity_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_quantity(self):
        """入力された数量を返す"""
        return self.quantity_input.value()

# primerの詳細画面のクラス
class PrimerManagerWindow(QMainWindow):
    def __init__(self, home_window):
        super().__init__()
        self.home_window = home_window
        self.setWindowTitle("プライマー管理")
        self.setGeometry(400, 400, 1200, 800)
        self.primer_data = sm.load_primers()
        self.member_list = sm.load_members()

        # UIセットアップ 
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.table = QTableWidget()
        main_layout.addWidget(self.table)

        menu_layout = QHBoxLayout()
        main_layout.addLayout(menu_layout)
    
        button_style = "QPushButton { font-size: 16px; padding: 12px 50px; }"

        add_button = QPushButton("追加")
        add_button.setStyleSheet(button_style)
        delete_button = QPushButton("削除")
        delete_button.setStyleSheet(button_style)
        back_button = QPushButton("ホームに戻る")
        back_button.setStyleSheet(button_style)

        menu_layout.addWidget(add_button)
        menu_layout.addWidget(delete_button)
        menu_layout.addStretch(1) 
        menu_layout.addWidget(back_button)

        # テーブル設定 
        self.table.setStyleSheet("""
            QTableWidget { font-size: 10pt; }
            QHeaderView::section { background-color: #F0F0F0; font-weight: bold; }
        """)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.update_table()

        #シグナル接続
        add_button.clicked.connect(self.add_item)
        delete_button.clicked.connect(self.delete_item)
        back_button.clicked.connect(self.go_home) 

    def update_table(self):
        self.table.clear()
        # カラムリストを固定定義（インデックスエラーを防ぐため重要）
        header = ["ID","Primer_Name","Application","Animal","Sequence", "Length", "Conc", "保存場所", "登録者", "登録日", "コメント"]
        self.table.setColumnCount(len(header))
        self.table.setHorizontalHeaderLabels(header)

        if not self.primer_data:
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(self.primer_data))

        for i, item in enumerate(self.primer_data):
            for j, key in enumerate(header):
                self.table.setItem(i, j, QTableWidgetItem(item.get(key, '')))
        
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive) # Length
        self.table.horizontalHeader().setSectionResizeMode(10, QHeaderView.ResizeMode.Interactive) # コメント(インデックス10)
        
        self.table.setColumnWidth(0, 70) #ID
        self.table.setColumnWidth(1, 160) #Primer_Name
        self.table.setColumnWidth(2, 100) #Application
        self.table.setColumnWidth(3, 100) #Animal
        self.table.setColumnWidth(4, 100) #Sequence
        self.table.setColumnWidth(5, 60) #Length
        self.table.setColumnWidth(6, 100) #Conc
        self.table.setColumnWidth(7, 100) #保存場所
        self.table.setColumnWidth(8, 80) #登録者
        self.table.setColumnWidth(9, 80) #登録日
        self.table.setColumnWidth(10, 200) #コメント
        
        # 追加: Mac等でウィンドウ幅を広げた時に最後の列が伸びるようにする
        self.table.horizontalHeader().setStretchLastSection(True)

    def add_item(self):
        """プライマー追加ダイアログを開く"""
        dialog = AddPrimerDialog(self.member_list, self)
        if dialog.exec():
            new_data = dialog.get_data()
            sm.add_primer_item(self.primer_data, new_data)
            self.update_table()

    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "選択エラー", "削除するプライマーを選択してください。")
            return
        
        item_to_delete = self.primer_data[selected_row]
        reply = QMessageBox.question(self, '確認', 
            f"プライマー「{item_to_delete.get('プライマー名')}」を削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            sm.delete_primer_item(self.primer_data, item_to_delete)
            self.update_table()
    
    def go_home(self):
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '確認', "変更を保存してホーム画面に戻りますか？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            sm.save_primers(self.primer_data)
            self.home_window.show()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            self.home_window.show()
            event.accept()
        else: # Cancel
            event.ignore()

# 凍結ストック検索ダイアログのクラス
class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("在庫検索")
        layout = QVBoxLayout(self)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("検索キーワード（細胞名）を入力")
        layout.addWidget(self.search_input)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_keyword(self):
        return self.search_input.text()

# 凍結ストック追加用のダイアログクラス
class AddDialog(QDialog):
    def __init__(self, member_list, all_locations, parent=None): 
        super().__init__(parent)
        self.all_locations = all_locations
        self.setWindowTitle("新規在庫追加")
        form_layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setRange(1, 999)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd") 
        
        self.saver_input = QComboBox()
        if member_list: 
            self.saver_input.addItems(member_list)
        
        self.species_input = QComboBox()
        self.species_input.addItems(["Human", "Mouse", "Rat", "Dog", "Cat", "Cow", "Other"])
        self.species_input.setEditable(True)
        
        self.cells_input = QComboBox()
        self.cells_input.addItems(["iPS", "ES", "Primary", "Somatic", "Other"])
        self.cells_input.setEditable(True) 

        self.passage_input = QComboBox()
        self.passage_input.addItems([str(i) for i in range(1, 9999)])
        self.passage_input.setEditable(True)
        
        self.cell_count_input = QLineEdit()
        self.cell_count_input.setPlaceholderText("例: 1.5e6 または unknown")
        
        location_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        self.location_input.setReadOnly(True)
        self.location_input.setPlaceholderText("ストック数を入力後、右のボタンから選択")
        location_button = QPushButton("場所を選択...")
        location_button.clicked.connect(self.open_location_dialog)
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(location_button)

        self.comment_input = QLineEdit()

        form_layout.addRow("細胞名:", self.name_input)
        form_layout.addRow("ストック数:", self.stock_input)
        form_layout.addRow("保存日:", self.date_input)
        form_layout.addRow("保存者:", self.saver_input)
        form_layout.addRow("種族:", self.species_input)
        form_layout.addRow("細胞種:", self.cells_input)
        form_layout.addRow("継代数:", self.passage_input)
        form_layout.addRow("細胞数:", self.cell_count_input)
        form_layout.addRow("保存場所:", location_layout)
        form_layout.addRow("コメント:", self.comment_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        form_layout.addWidget(button_box)

    def open_location_dialog(self):
        stock_count = self.stock_input.value()
        if stock_count <= 0:
            QMessageBox.warning(self, "入力エラー", "先にストック数を1以上に設定してください。")
            return
        dialog = LocationDialog(stock_count, self.all_locations, self)
        if dialog.exec():
            locations = dialog.get_locations()
            self.location_input.setText(", ".join(locations))

    def get_data(self):
        return {
            "細胞名": self.name_input.text(),
            "ストック数": self.stock_input.value(),
            "保存日": self.date_input.date().toString("yyyy-MM-dd"),
            "保存者": self.saver_input.currentText(),
            "種族": self.species_input.currentText(),
            "細胞種": self.cells_input.currentText(),
            "継代数": self.passage_input.currentText(),
            "細胞数": self.cell_count_input.text(),
            "保存場所": self.location_input.text(),
            "コメント": self.comment_input.text()
        }

# メンバー管理用のダイアログクラス
class MemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("メンバー管理")
        self.members = sm.load_members()

        main_layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.members)
        main_layout.addWidget(self.list_widget)

        edit_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("新しい名前を入力")
        add_button = QPushButton("追加")
        delete_button = QPushButton("削除")
        edit_layout.addWidget(self.name_input)
        edit_layout.addWidget(add_button)
        edit_layout.addWidget(delete_button)
        main_layout.addLayout(edit_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        main_layout.addWidget(button_box)

        add_button.clicked.connect(self.add_member)
        delete_button.clicked.connect(self.delete_member)
        button_box.rejected.connect(self.reject)

    def add_member(self):
        name = self.name_input.text().strip()
        if name and name not in self.members:
            self.members.append(name)
            self.list_widget.addItem(name)
            self.name_input.clear()
            sm.save_members(self.members)

    def delete_member(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "選択エラー", "削除する名前を選択してください。")
            return
        
        name_to_delete = selected_item.text()
        reply = QMessageBox.question(self, "確認", f"「{name_to_delete}」を削除しますか？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.members.remove(name_to_delete)
            self.list_widget.takeItem(self.list_widget.row(selected_item))
            sm.save_members(self.members)

# 使用者選択用のダイアログクラス
class SelectUserDialog(QDialog):
    def __init__(self, member_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用者を選択")
        
        layout = QFormLayout(self)
        
        self.user_combo = QComboBox()
        self.user_combo.addItems(member_list)
        
        layout.addRow("使用者:", self.user_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)

    def get_selected_user(self):
        return self.user_combo.currentText()

# 凍結ストックのタンクの場所選択用のカスタムダイアログクラス
class LocationDialog(QDialog):
    def __init__(self, required_count, all_locations, parent=None):
        super().__init__(parent)
        self.setWindowTitle("保存場所を選択")
        self.setMinimumSize(1000, 750)
        self.required_count = required_count 
        self.all_locations = all_locations 

        self.selected_canister = None
        self.selected_rack = None
        self.final_locations = [] 

        # --- UIのセットアップ ---
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        
        canister_layout = QGridLayout()
        self.canister_buttons = {}
        positions = [(0, 1, "1"), (0, 2, "2"), (1, 3, "3"), (2, 2, "4"), (2, 1, "5"), (1, 0, "6")]
        for row, col, label in positions:
            button = QPushButton(label)
            button.setFixedSize(80, 80)
            button.clicked.connect(lambda checked, l=label: self.on_canister_selected(l))
            canister_layout.addWidget(button, row, col)
            self.canister_buttons[label] = button
        left_layout.addLayout(canister_layout)

        rack_layout = QVBoxLayout()
        self.rack_buttons = {}
        rack_labels = ["1", "2", "3", "4", "5"]
        for label in rack_labels:
            button = QPushButton(label)
            button.clicked.connect(lambda checked, l=label: self.on_rack_selected(l))
            rack_layout.addWidget(button)
            self.rack_buttons[label] = button
        left_layout.addLayout(rack_layout)

        self.box_table = QTableWidget(10, 10)
        self.box_table.setFrameStyle(QFrame.Shape.NoFrame)
        self.delegate = HighlightDelegate(self.box_table)
        self.box_table.setItemDelegate(self.delegate)

        
        self.box_table.setStyleSheet("QHeaderView::section { font-size: 14pt; }")
        self.box_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
      
        cell_size = 45
        self.box_table.horizontalHeader().setDefaultSectionSize(cell_size)
        self.box_table.verticalHeader().setDefaultSectionSize(cell_size)
        self.box_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.box_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.box_table.setHorizontalHeaderLabels([str(i) for i in range(1, 11)])
        self.box_table.setVerticalHeaderLabels([chr(ord('A') + i) for i in range(10)])
        self.box_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.box_table.itemSelectionChanged.connect(self.on_box_pos_selected) 

        self.info_label = QLabel(f"必要な選択数: {self.required_count}")
        self.result_label = QLabel("選択結果: -")
        self.result_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # OKボタンへの参照を取得し、初期状態を無効にする
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        button_box.accepted.connect(self.on_ok)
        button_box.rejected.connect(self.reject)

        main_layout.addLayout(left_layout)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.info_label)
        right_layout.addWidget(self.box_table)
        right_layout.addWidget(self.result_label)
        right_layout.addWidget(button_box)
        main_layout.addLayout(right_layout)

    def on_canister_selected(self, label):
        self.selected_canister = label
        # 全てのキャニスターボタンのスタイルをリセット
        for btn in self.canister_buttons.values():
            btn.setStyleSheet("") 
        # 選択されたボタンだけ色を濃くする
        self.canister_buttons[label].setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        
        self.box_table.clearSelection()
        self.refresh_box_table() 
        self.update_result_label()

    def on_rack_selected(self, label):
        self.selected_rack = label
        # 全てのラックボタンのスタイルをリセット
        for btn in self.rack_buttons.values():
            btn.setStyleSheet("")
        # 選択されたボタンだけ色を濃くする
        self.rack_buttons[label].setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")

        self.box_table.clearSelection()
        self.refresh_box_table()
        self.update_result_label()
    
    def on_box_pos_selected(self):
        self.update_result_label()

    def update_result_label(self):
        c = self.selected_canister or "?"
        r = self.selected_rack or "?"
        
        # 重複を除いたユニークなインデックスで選択数をカウント
        unique_indexes = {(idx.row(), idx.column()) for idx in self.box_table.selectedIndexes()}
        b_count = 0
        for row, col in unique_indexes:
            item = self.box_table.item(row, col)
            # 使用不可（灰色）セルはカウントしない
            if item and not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                continue
            b_count += 1
            
        self.result_label.setText(f"選択結果: {c}-{r} に {b_count}個選択済み")
        
        # 条件が満たされた場合のみOKボタンを有効化
        if b_count == self.required_count and self.selected_canister and self.selected_rack:
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def refresh_box_table(self):
        self.box_table.clearContents()
        if not self.selected_canister or not self.selected_rack:
            return

        used_color = QColor("#555555")
        for item_locations in self.all_locations:
            locations = [loc.strip() for loc in item_locations.split(',') if loc.strip()]
            for loc in locations:
                parts = loc.split('-')
                if len(parts) != 3: continue
                canister, rack, pos_str = parts
                if self.selected_canister == canister and self.selected_rack == rack:
                    row, col = self.parse_location(pos_str)
                    if row is not None and col is not None:
                        cell_item = QTableWidgetItem()
                        cell_item.setData(Qt.ItemDataRole.BackgroundRole, used_color)
                        cell_item.setFlags(cell_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                        self.box_table.setItem(row, col, cell_item)

    def on_ok(self):
        self.selected_box_positions = []
        # 重複を除いたユニークなインデックスを取得
        unique_indexes = {(idx.row(), idx.column()) for idx in self.box_table.selectedIndexes()}

        for row, col in unique_indexes:
            item = self.box_table.item(row, col)
            # 安全策：itemがNoneの場合は未初期化（空）セルなので、使用可能とみなす
            is_disabled = False
            if item and not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                is_disabled = True
            
            if is_disabled:
                continue
            self.selected_box_positions.append(f"{chr(ord('A') + row)}{col + 1}")

        # 念のため最終チェック（基本的にはOKボタンの制御で防がれる）
        if len(self.selected_box_positions) != self.required_count:
            QMessageBox.warning(self, "選択エラー", f"選択数({len(self.selected_box_positions)})とストック数({self.required_count})が一致しません。")
            return

        base = f"{self.selected_canister}-{self.selected_rack}"
        # 結果の順序を一定にするためにソートする
        self.final_locations = [f"{base}-{pos}" for pos in sorted(self.selected_box_positions)]
        self.accept()

    def parse_location(self, pos_str):
        if not pos_str or len(pos_str) < 2: return None, None
        row_char = pos_str[0].upper()
        col_str = pos_str[1:]
        if 'A' <= row_char <= 'J' and col_str.isdigit():
            row = ord(row_char) - ord('A')
            col = int(col_str) - 1
            if 0 <= col < 10:
                return row, col
        return None, None

    def get_locations(self): 
        return self.final_locations

#タンクの在庫使用時のダイアログ
class UseLocationDialog(QDialog):
    def __init__(self, locations_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用するストックの場所を選択")
        self.setMinimumSize(700, 800)

        self.used_locations = []
        
        self.occupied_color = QColor("#aaddff") # 在庫ありの色
        self.selected_color = QColor("#3498db") # 選択中の色

        layout = QVBoxLayout(self)
        self.box_table = QTableWidget(10, 10)

        first_location = locations_str.split(',')[0].strip()
        prefix = "-".join(first_location.split('-')[:-1]) if '-' in first_location else "場所情報なし"

        self.location_info_label = QLabel(f"表示中の場所: {prefix}")
        self.location_info_label.setStyleSheet("""
        QLabel {
        font-size: 16pt;
        margin-bottom: 10px;
        }
                                                """)

        self.box_table.setFrameStyle(QFrame.Shape.NoFrame)
        self.delegate = HighlightDelegate(self.box_table)
        self.box_table.setItemDelegate(self.delegate)

       
        self.box_table.setStyleSheet("QHeaderView::section { font-size: 14pt; padding: 0px; }")
        self.box_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        cell_size = 45
        self.box_table.horizontalHeader().setDefaultSectionSize(cell_size)
        self.box_table.verticalHeader().setDefaultSectionSize(cell_size)
        self.box_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.box_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.box_table.setHorizontalHeaderLabels([str(i) for i in range(1, 11)])
        self.box_table.setVerticalHeaderLabels([chr(ord('A') + i) for i in range(10)])
        self.box_table.cellClicked.connect(self.on_cell_clicked)
        
        self.info_label = QLabel("在庫がある場所（水色）から、使用するものをクリックしてください。")
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.location_info_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.box_table)
        layout.addWidget(button_box)

        self.highlight_occupied_cells(locations_str)

    def parse_location(self, pos_str):
        if not pos_str or len(pos_str) < 2: return None, None
        row_char = pos_str[0].upper()
        col_str = pos_str[1:]
        if 'A' <= row_char <= 'J' and col_str.isdigit():
            row = ord(row_char) - ord('A')
            col = int(col_str) - 1
            return row, col
        return None, None

    def highlight_occupied_cells(self, locations_str):
        locations = [loc.strip() for loc in locations_str.split(',') if loc.strip()]
        for loc in locations:
            pos_str = loc.split('-')[-1]
            row, col = self.parse_location(pos_str)
            if row is not None and col is not None:
                item = QTableWidgetItem() 
                item.setData(Qt.ItemDataRole.BackgroundRole, self.occupied_color)
                self.box_table.setItem(row, col, item)

    def on_cell_clicked(self, row, column):
        item = self.box_table.item(row, column)
        if item is None:
            return 

        current_color = item.data(Qt.ItemDataRole.BackgroundRole)
        if current_color not in [self.occupied_color, self.selected_color]:
            return
        
        pos_str = f"{chr(ord('A') + row)}{column + 1}"
        
        if current_color == self.occupied_color:
            item.setData(Qt.ItemDataRole.BackgroundRole, self.selected_color) # 選択状態にする
            if pos_str not in self.used_locations: self.used_locations.append(pos_str)
        else:
            item.setData(Qt.ItemDataRole.BackgroundRole, self.occupied_color) # 選択を解除する
            if pos_str in self.used_locations: self.used_locations.remove(pos_str)
            
    def get_used_locations(self):
        return self.used_locations

#ログファイルの内容をテーブルで表示するダイアログ
class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("操作ログ閲覧")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.load_log_data()

    def load_log_data(self):
        try:

            with open(sm.LOG_FILENAME, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f)
                
                header = next(reader, None)
                if header is None: return 
                
                self.table.setColumnCount(len(header))
                self.table.setHorizontalHeaderLabels(header)

                data = list(reader)
                self.table.setRowCount(len(data))

                for row_index, row_data in enumerate(data):
                    for col_index, col_data in enumerate(row_data):
                        item = QTableWidgetItem(col_data)
                        self.table.setItem(row_index, col_index, item)
            
            self.table.resizeColumnsToContents()

        except FileNotFoundError:
            QMessageBox.warning(self, "エラー", "ログファイルが見つかりません。")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ログの読み込み中にエラーが発生しました:\n{e}")

# プライマーの保存画面にダイアログ
class AddPrimerDialog(QDialog):
    def __init__(self, member_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新規プライマー追加")
        self.setMinimumWidth(500) 

        form_layout = QFormLayout(self)
        
        #入力ウィジェットの作成
        self.id_input = QLineEdit()

        self.name_input = QLineEdit()

        self.app_input = QComboBox()
        self.app_input.addItems(["RT-PCR","Q-RT-PCR","GenomicPCR","Constraction","Bisulfite-PCR"])
        self.app_input.setEditable(True)

        self.animal_input = QComboBox()
        self.animal_input.addItems(["Human","dog","mouse"])
        self.animal_input.setEditable(True)

        self.sequence_input = QLineEdit()
        self.sequence_input.setFont(QFont("Courier New", 10)) 

        self.length_label = QLabel("0 bp")

        self.conc_value_input = QLineEdit() # 数値入力用
        self.conc_unit_input = QComboBox()  # 単位選択用
        self.conc_unit_input.addItems(["µM","nM","mM","M"]) 
        conc_layout = QHBoxLayout()
        conc_layout.addWidget(self.conc_value_input)
        conc_layout.addWidget(self.conc_unit_input)
        self.conc_unit_input.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
   
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("例: Primer Box 1")

        self.registrant_input = QComboBox()
        if member_list:
            self.registrant_input.addItems(member_list)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        
        self.comment_input = QLineEdit()

        # レイアウトへの追加 
        form_layout.addRow("ID:",self.id_input)
        form_layout.addRow("Primer_Name", self.name_input)
        form_layout.addRow("Application",self.app_input)
        form_layout.addRow("Animal",self.animal_input)
        form_layout.addRow("Sequence", self.sequence_input)
        form_layout.addRow("Length", self.length_label)
        form_layout.addRow("Conc",conc_layout)       
        form_layout.addRow("保存場所:", self.location_input)
        form_layout.addRow("コメント:", self.comment_input)

        #ボタン 
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        form_layout.addWidget(button_box)
        
        # 配列が変更されるたびに長さを更新する
        self.sequence_input.textChanged.connect(self.update_length)

    def update_length(self, text):
        # A, T, G, C, U, N 以外の文字は無視してカウント
        valid_bases = "ATGCUNatgcun"
        seq_len = len([base for base in text if base in valid_bases])
        self.length_label.setText(f"{seq_len} bp")

    def get_data(self):
        concentration = f"{self.conc_value_input.text()} {self.conc_unit_input.currentText()}"
        return {
            "ID":self.id_input.text(),
            "Primer_Name": self.name_input.text(),
            "Application":self.app_input.currentText(),
            "Animal":self.animal_input.currentText(),
            "Sequence": self.sequence_input.text(), 
            "Length": self.length_label.text(),
            "Conc": concentration,
            "保存場所": self.location_input.text(),
            "登録者": self.registrant_input.currentText(),
            "登録日": self.date_input.date().toString("yyyy-MM-dd"),
            "コメント": self.comment_input.text()
        }

#背景色を描画するデリゲート
class HighlightDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # このセルに「背景色」のデータが設定されているか確認
        background_color = index.data(Qt.ItemDataRole.BackgroundRole)
        
        if background_color is not None:
            #もしあれば、まずその色で背景を完全に塗りつぶす
            painter.fillRect(option.rect, QColor(background_color))
        
        #残りの描画は親クラスの標準メソッドに任せる
        super().paint(painter, option, index)


if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)


    app.setStyle('Fusion')
    
    if platform.system() == 'Darwin':

        font = QFont("Hiragino Sans", 14)
    else:

        font = QFont("Meiryo", 12) 
    
    app.setFont(font)

    # WindowsでもMacでも全く同じインシリコ・デザインを適用
    app.setStyleSheet("""
        QMainWindow, QDialog { background-color: #F4F6F9; }
        
        /* 💡文字が細く見えないように全体の文字色を真っ黒(#333333)にする */
        QWidget { color: #333333; }
        
        QTableWidget { 
            background-color: #FFFFFF; 
            alternate-background-color: #EAF1F8; /* 1行ごとの薄いブルーストライプ */
            selection-background-color: #3498DB; /* 選択時は綺麗なブルー */
            border: 1px solid #D1D9E6; 
        }
        /* ヘッダーも少し太字にしてしっかりさせる */
        QHeaderView::section {
            font-weight: bold;
            color: #25405B;
        }
    """)

    window = HomeWindow()
    window.show()
    sys.exit(app.exec())