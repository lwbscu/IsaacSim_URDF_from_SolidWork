import sys
import os
import re
import shutil
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QComboBox)
from PyQt5.QtGui import QFont

class URDFCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
        self.lang = 'zh' 
        self.setup_i18n()
        self.initUI()

    def setup_i18n(self):
        """配置中英文本字典"""
        self.t = {
            'zh': {
                'title': 'Isaac Sim URDF 资产清洗专家',
                'lbl_target_dir': '目标所在文件夹路径:',
                'ph_target_dir': '请选择或粘贴资产的根目录路径...',
                'btn_browse': '浏览...',
                'lbl_old_urdf': '原urdf路径:',
                'ph_old_urdf': '请选择或粘贴原 .urdf 文件的完整路径...',
                'lbl_new_name': '期望改名后的urdf名称:',
                'ph_new_name': '例如: robot_test (纯英文/下划线，无需加后缀)',
                'btn_scan': '1. 深度扫描 (Scan)',
                'btn_clean': '2. 一键清洗重构 (Clean)',
                'btn_check': '3. 关节拓扑分析 (Check Joints)',
                'btn_clear': '清空日志',
                'err_title': '错误',
                'err_no_dir': '请提供有效的目标所在文件夹路径！',
                'err_no_input': '清洗操作必须提供【原urdf路径】和【期望改名后的名称】！',
                'err_bad_name': '新资产名不符合 USD 规范 (不能包含中文、空格或连字符)！',
                'log_scan_start': '开始执行深度扫描: ',
                'log_clean_start': '开始执行资产清洗重构作业...',
                'log_check_start': '开始解析 URDF 关节拓扑结构...'
            },
            'en': {
                'title': 'Isaac Sim URDF Asset Cleaner',
                'lbl_target_dir': 'Target Folder Path:',
                'ph_target_dir': 'Select or paste the asset root directory...',
                'btn_browse': 'Browse...',
                'lbl_old_urdf': 'Original URDF Path:',
                'ph_old_urdf': 'Select or paste the full path of the original .urdf...',
                'lbl_new_name': 'Expected New URDF Name:',
                'ph_new_name': 'e.g., robot_test (English/Underscore only, no extension)',
                'btn_scan': '1. Deep Scan',
                'btn_clean': '2. One-Click Clean & Rebuild',
                'btn_check': '3. Check Joint Topology',
                'btn_clear': 'Clear Log',
                'err_title': 'Error',
                'err_no_dir': 'Please provide a valid target folder path!',
                'err_no_input': 'Both [Original URDF Path] and [New URDF Name] are required for cleaning!',
                'err_bad_name': 'New name violates USD specs (No Chinese, spaces, or hyphens allowed)!',
                'log_scan_start': 'Starting Deep Scan: ',
                'log_clean_start': 'Starting Asset Clean & Rebuild...',
                'log_check_start': 'Analyzing URDF Joint Topology...'
            }
        }

    def initUI(self):
        self.resize(900, 600)
        layout = QVBoxLayout()

        # --- 语言切换区 ---
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.lbl_lang = QLabel("🌐 Language / 语言: ")
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["简体中文", "English"])
        self.cb_lang.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addWidget(self.cb_lang)
        layout.addLayout(lang_layout)

        # --- 输入网格区 ---
        grid = QGridLayout()
        
        self.lbl_dir = QLabel()
        grid.addWidget(self.lbl_dir, 0, 0)
        self.dir_input = QLineEdit()
        grid.addWidget(self.dir_input, 0, 1)
        self.btn_browse_dir = QPushButton()
        self.btn_browse_dir.clicked.connect(self.browse_folder)
        grid.addWidget(self.btn_browse_dir, 0, 2)

        self.lbl_old = QLabel()
        grid.addWidget(self.lbl_old, 1, 0)
        self.old_urdf_input = QLineEdit()
        grid.addWidget(self.old_urdf_input, 1, 1)
        self.btn_browse_urdf = QPushButton()
        self.btn_browse_urdf.clicked.connect(self.browse_urdf_file)
        grid.addWidget(self.btn_browse_urdf, 1, 2)

        self.lbl_new = QLabel()
        grid.addWidget(self.lbl_new, 2, 0)
        self.new_name_input = QLineEdit()
        grid.addWidget(self.new_name_input, 2, 1)

        layout.addLayout(grid)

        # --- 操作按钮区 ---
        btn_layout = QHBoxLayout()
        self.btn_scan = QPushButton()
        self.btn_scan.clicked.connect(self.run_scan)
        
        self.btn_clean = QPushButton()
        self.btn_clean.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_clean.clicked.connect(self.run_clean)
        
        self.btn_check = QPushButton()
        self.btn_check.clicked.connect(self.run_check)

        self.btn_clear_log = QPushButton()
        self.btn_clear_log.clicked.connect(lambda: self.log_area.clear())
        
        btn_layout.addWidget(self.btn_scan)
        btn_layout.addWidget(self.btn_clean)
        btn_layout.addWidget(self.btn_check)
        btn_layout.addWidget(self.btn_clear_log)
        layout.addLayout(btn_layout)

        # --- 日志输出区 ---
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        self.log_area.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.update_ui_texts() 

    def change_language(self, index):
        self.lang = 'en' if index == 1 else 'zh'
        self.update_ui_texts()

    def update_ui_texts(self):
        texts = self.t[self.lang]
        self.setWindowTitle(texts['title'])
        self.lbl_dir.setText(texts['lbl_target_dir'])
        self.dir_input.setPlaceholderText(texts['ph_target_dir'])
        self.btn_browse_dir.setText(texts['btn_browse'])
        
        self.lbl_old.setText(texts['lbl_old_urdf'])
        self.old_urdf_input.setPlaceholderText(texts['ph_old_urdf'])
        self.btn_browse_urdf.setText(texts['btn_browse'])
        
        self.lbl_new.setText(texts['lbl_new_name'])
        self.new_name_input.setPlaceholderText(texts['ph_new_name'])
        
        self.btn_scan.setText(texts['btn_scan'])
        self.btn_clean.setText(texts['btn_clean'])
        self.btn_check.setText(texts['btn_check'])
        self.btn_clear_log.setText(texts['btn_clear'])

    def log(self, message):
        self.log_area.append(message)
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t[self.lang]['btn_browse'])
        if folder: self.dir_input.setText(folder)

    def browse_urdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.t[self.lang]['lbl_old_urdf'], "", "URDF Files (*.urdf);;All Files (*)")
        if file_path:
            self.old_urdf_input.setText(file_path)
            if not self.dir_input.text():
                parent_dir = os.path.dirname(file_path)
                if os.path.basename(parent_dir) == 'urdf':
                    self.dir_input.setText(os.path.dirname(parent_dir))
                else:
                    self.dir_input.setText(parent_dir)

    def validate_inputs(self, check_names=False):
        texts = self.t[self.lang]
        target_dir = self.dir_input.text().strip()
        if not target_dir or not os.path.exists(target_dir):
            QMessageBox.warning(self, texts['err_title'], texts['err_no_dir'])
            return False
        
        if check_names:
            old_urdf = self.old_urdf_input.text().strip()
            new_name = self.new_name_input.text().strip()
            if not old_urdf or not new_name:
                QMessageBox.warning(self, texts['err_title'], texts['err_no_input'])
                return False
            
            new_name_base = os.path.splitext(os.path.basename(new_name))[0]
            if self.chinese_pattern.search(new_name_base) or ' ' in new_name_base or '-' in new_name_base:
                QMessageBox.warning(self, texts['err_title'], texts['err_bad_name'])
                return False
        return True

    def run_scan(self):
        if not self.validate_inputs(): return
        target_dir = self.dir_input.text().strip()
        
        self.log("\n" + "="*50)
        self.log(self.t[self.lang]['log_scan_start'] + target_dir)
        self.log("="*50)

        bad_naming_count = 0
        for root, dirs, files in os.walk(target_dir):
            for name in dirs + files:
                if self.chinese_pattern.search(name) or ' ' in name or '-' in name:
                    self.log(f"[Bad Naming] {os.path.relpath(os.path.join(root, name), target_dir)}")
                    bad_naming_count += 1
        
        urdf_files = [os.path.join(r, f) for r, d, files in os.walk(target_dir) for f in files if f.endswith(('.urdf', '.xacro'))]
        for urdf_path in urdf_files:
            self.log(f"\n--- [Target URDF]: {os.path.relpath(urdf_path, target_dir)} ---")
            with open(urdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            pkg_count = content.count('package://')
            if pkg_count > 0: self.log(f"[*] Found {pkg_count} 'package://' absolute paths.")

            matches = re.compile(r'(name|filename)="([^"]+)"').findall(content)
            bad_attrs = {f'{k}="{v}"' for k, v in matches if self.chinese_pattern.search(v) or '-' in v or ' ' in v}
            if bad_attrs:
                self.log(f"[*] Found {len(bad_attrs)} invalid attributes (Chinese/hyphens/spaces).")
                for bad in list(bad_attrs)[:5]: self.log(f"    -> {bad}")
        self.log("="*50 + "\n[Scan Complete]")

    def run_clean(self):
        if not self.validate_inputs(check_names=True): return
        target_dir = self.dir_input.text().strip()
        old_name = os.path.splitext(os.path.basename(self.old_urdf_input.text().strip()))[0]
        new_name = os.path.splitext(os.path.basename(self.new_name_input.text().strip()))[0]

        self.new_name_input.setText(new_name)

        self.log("\n" + "="*50)
        self.log(self.t[self.lang]['log_clean_start'])
        self.log("="*50)

        cache_dir = os.path.join(target_dir, "urdf", old_name)
        if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
            shutil.rmtree(cache_dir)
            self.log(f"[Clean] Removed USD cache: {cache_dir}")

        rename_count = 0
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for name in files + dirs:
                if old_name in name:
                    new_filename = name.replace(old_name, new_name)
                    os.rename(os.path.join(root, name), os.path.join(root, new_filename))
                    rename_count += 1
                    self.log(f"[Rename] {name} => {new_filename}")

        if rename_count == 0:
            self.log("[Error] No files matched the Original URDF Name!")
            return

        urdf_path = os.path.join(target_dir, "urdf", f"{new_name}.urdf")
        if not os.path.exists(urdf_path):
            self.log(f"[Error] Cannot find target URDF: {urdf_path}")
            return

        with open(urdf_path, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace(old_name, new_name)
        pkg_count = content.count(f"package://{new_name}/")
        content = content.replace(f"package://{new_name}/", "../")
        with open(urdf_path, 'w', encoding='utf-8') as f: f.write(content)
        
        self.log(f"[Rebuild] Replaced {pkg_count} 'package://' with relative paths '../'")
        self.log("="*50 + "\n[Clean & Rebuild Complete! Ready for Isaac Sim]")

    def run_check(self):
        if not self.validate_inputs(): return
        target_dir = self.dir_input.text().strip()
        
        self.log("\n" + "="*50)
        self.log(self.t[self.lang]['log_check_start'])
        self.log("="*50)

        urdf_files = [os.path.join(r, f) for r, d, files in os.walk(target_dir) for f in files if f.endswith('.urdf')]
        if not urdf_files: return
            
        urdf_path = urdf_files[0]
        try:
            joints = ET.parse(urdf_path).getroot().findall('joint')
            self.log(f"[Total Joints] {len(joints)}\n")
            
            joint_dict = {}
            for j in joints:
                joint_dict.setdefault(j.get('type'), []).append(j.get('name'))
            
            for j_type, names in joint_dict.items():
                self.log(f"=== Type: {j_type.upper()} ({len(names)}) ===")
                for name in names: self.log(f"  - {name}")
                self.log("")
        except Exception as e:
            self.log(f"[Error] {e}")
        self.log("="*50)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = URDFCleanerApp()
    ex.show()
    sys.exit(app.exec_())
