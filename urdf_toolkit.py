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

                'log_scan_start': '开始执行深度扫描: {0}',
                'scan_bad_name': '  [发现非法物理命名] {0}',
                'scan_all_good': '  -> [正常] 所有物理文件命名合规。',
                'scan_no_urdf': '  [警告] 未发现 .urdf 文件！',
                'scan_target': '\n--- 分析目标: {0} ---',
                'scan_pkg_found': '  [发现隔离墙] 找到 {0} 处 \'package://\' 绝对路径引用。',
                'scan_pkg_none': '  -> [正常] 未发现绝对路径。',
                'scan_attr_found': '  [发现非法字符] 找到 {0} 处违规属性(中文/空格/连字符)。',
                'scan_attr_none': '  -> [正常] 内部属性命名纯净。',
                'scan_complete': '[扫描完毕]',

                'log_clean_start': '开始执行资产清洗重构作业...',
                'clean_cache_rm': '[清理] 销毁废弃 USD 缓存: {0}',
                'clean_rename': '[重命名] {0} => {1}',
                'clean_rename_done': '--- 内部物理重命名完成，共 {0} 项 ---',
                'clean_err_no_match': '[致命错误] 没有找到任何匹配原资产名的文件！',
                'clean_err_no_target': '[致命错误] 找不到目标 URDF 文件: {0}',
                'clean_rebuild': '[重构] 成功将 {0} 处 \'package://\' 替换为相对路径 \'../\'',
                'clean_root_rename': '[根目录更名] {0} => {1}',
                'clean_complete': '[清洗与重构完美结束！可直接导入 Isaac Sim]',

                'log_check_start': '开始解析 URDF 关节拓扑结构...',
                'chk_no_urdf': '[错误] 当前目录及子目录未找到 .urdf 文件。',
                'chk_analyzing': '正在分析: {0}\n',
                'chk_total': '[总体统计] 共定义了 {0} 个 joint。\n',
                'chk_type': '=== 类型: {0} ({1} 个) ===',
                'chk_warn_fixed': '  (警告: fixed 无自由度，Isaac Sim Stage 树中不可见)',
                'chk_suspect_head': '=== 运动件漏检排查 (轮子/夹爪) ===',
                'chk_suspect_found': '  -> 发现特征关节: {0} (当前类型: {1})',
                'chk_suspect_none': '  -> 未发现明显包含 wheel/gripper/finger 等特征词的关节。',
                'chk_err': '[解析出错] {0}'
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

                'log_scan_start': 'Starting Deep Scan: {0}',
                'scan_bad_name': '  [Bad Naming] {0}',
                'scan_all_good': '  -> [OK] All physical file names are USD-compliant.',
                'scan_no_urdf': '  [Warning] No .urdf files found!',
                'scan_target': '\n--- [Target URDF]: {0} ---',
                'scan_pkg_found': '  [*] Found {0} \'package://\' absolute paths.',
                'scan_pkg_none': '  -> [OK] No absolute paths found.',
                'scan_attr_found': '  [*] Found {0} invalid attributes (Chinese/hyphens/spaces).',
                'scan_attr_none': '  -> [OK] Inner attributes are clean.',
                'scan_complete': '[Scan Complete]',

                'log_clean_start': 'Starting Asset Clean & Rebuild...',
                'clean_cache_rm': '[Clean] Removed USD cache: {0}',
                'clean_rename': '[Rename] {0} => {1}',
                'clean_rename_done': '--- Internal physical rename complete. {0} items renamed ---',
                'clean_err_no_match': '[Fatal Error] No files matched the Original URDF Name!',
                'clean_err_no_target': '[Fatal Error] Cannot find target URDF: {0}',
                'clean_rebuild': '[Rebuild] Replaced {0} \'package://\' with relative paths \'../\'',
                'clean_root_rename': '[Root Rename] {0} => {1}',
                'clean_complete': '[Clean & Rebuild Complete! Ready for Isaac Sim]',

                'log_check_start': 'Analyzing URDF Joint Topology...',
                'chk_no_urdf': '[Error] No .urdf files found in the directory.',
                'chk_analyzing': 'Analyzing: {0}\n',
                'chk_total': '[Total Joints] {0} joints defined.\n',
                'chk_type': '=== Type: {0} ({1}) ===',
                'chk_warn_fixed': '  (Warning: fixed joints have no DOF, hidden in Isaac Sim Stage)',
                'chk_suspect_head': '=== Missing Parts Check (Wheels/Grippers) ===',
                'chk_suspect_found': '  -> Found suspect joint: {0} (Current Type: {1})',
                'chk_suspect_none': '  -> No typical wheel/gripper/finger joints found.',
                'chk_err': '[Parsing Error] {0}'
            }
        }

    def initUI(self):
        self.resize(900, 600)
        layout = QVBoxLayout()

        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.lbl_lang = QLabel("🌐 Language / 语言: ")
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["简体中文", "English"])
        self.cb_lang.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addWidget(self.cb_lang)
        layout.addLayout(lang_layout)

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

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        self.log_area.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.update_ui_texts() 
        self.show_welcome_message()

    def show_welcome_message(self):
        self.log_area.clear()
        welcome_text = (
            "🚀 欢迎使用 Isaac Sim URDF 资产清洗专家！\n"
            "   Welcome to Isaac Sim URDF Asset Cleaner!\n\n"
            "【使用指南 / How to Use】\n"
            "  1. 点击【浏览】选择目标文件夹和原 URDF 文件。\n"
            "     Click [Browse] to select Target Folder & Original URDF.\n"
            "  2. 填写纯英文的【期望改名后的urdf名称】（无需加后缀）。\n"
            "     Input the [Expected New URDF Name] (English/Underscores only).\n"
            "  3. 依次点击按钮：1. 扫描 -> 2. 清洗 -> 3. 关节分析。\n"
            "     Click buttons sequentially: 1. Scan -> 2. Clean -> 3. Check Joints.\n"
            "=================================================="
        )
        self.log(welcome_text)

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
        texts = self.t[self.lang]
        target_dir = self.dir_input.text().strip()

        self.log("\n" + "="*50)
        self.log(texts['log_scan_start'].format(target_dir))
        self.log("="*50)

        bad_naming_count = 0
        for root, dirs, files in os.walk(target_dir):
            for name in dirs + files:
                if self.chinese_pattern.search(name) or ' ' in name or '-' in name:
                    self.log(texts['scan_bad_name'].format(os.path.relpath(os.path.join(root, name), target_dir)))
                    bad_naming_count += 1

        if bad_naming_count == 0:
            self.log(texts['scan_all_good'])

        urdf_files = [os.path.join(r, f) for r, d, files in os.walk(target_dir) for f in files if f.endswith(('.urdf', '.xacro'))]
        if not urdf_files:
            self.log(texts['scan_no_urdf'])
            return

        for urdf_path in urdf_files:
            self.log(texts['scan_target'].format(os.path.relpath(urdf_path, target_dir)))
            with open(urdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            pkg_count = content.count('package://')
            if pkg_count > 0: 
                self.log(texts['scan_pkg_found'].format(pkg_count))
            else:
                self.log(texts['scan_pkg_none'])

            matches = re.compile(r'(name|filename)="([^"]+)"').findall(content)
            bad_attrs = {f'{k}="{v}"' for k, v in matches if self.chinese_pattern.search(v) or '-' in v or ' ' in v}
            if bad_attrs:
                self.log(texts['scan_attr_found'].format(len(bad_attrs)))
                for bad in list(bad_attrs)[:5]: self.log(f"    -> {bad}")
            else:
                self.log(texts['scan_attr_none'])

        self.log("="*50 + "\n" + texts['scan_complete'])

    def run_clean(self):
        if not self.validate_inputs(check_names=True): return
        texts = self.t[self.lang]
        target_dir = self.dir_input.text().strip()
        old_name = os.path.splitext(os.path.basename(self.old_urdf_input.text().strip()))[0]
        new_name = os.path.splitext(os.path.basename(self.new_name_input.text().strip()))[0]

        self.new_name_input.setText(new_name)

        self.log("\n" + "="*50)
        self.log(texts['log_clean_start'])
        self.log("="*50)

        cache_dir = os.path.join(target_dir, "urdf", old_name)
        if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
            shutil.rmtree(cache_dir)
            self.log(texts['clean_cache_rm'].format(cache_dir))

        rename_count = 0
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for name in files + dirs:
                if old_name in name:
                    new_filename = name.replace(old_name, new_name)
                    os.rename(os.path.join(root, name), os.path.join(root, new_filename))
                    rename_count += 1
                    self.log(texts['clean_rename'].format(name, new_filename))
        self.log(texts['clean_rename_done'].format(rename_count))

        if rename_count == 0:
            self.log(texts['clean_err_no_match'])
            return

        urdf_path = os.path.join(target_dir, "urdf", f"{new_name}.urdf")
        if not os.path.exists(urdf_path):
            self.log(texts['clean_err_no_target'].format(urdf_path))
            return

        with open(urdf_path, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace(old_name, new_name)
        pkg_count = content.count(f"package://{new_name}/")
        content = content.replace(f"package://{new_name}/", "../")
        with open(urdf_path, 'w', encoding='utf-8') as f: f.write(content)
        self.log(texts['clean_rebuild'].format(pkg_count))

        try:
            tree = ET.parse(urdf_path)
            root = tree.getroot()
            healed = False
            urdf_dir = os.path.dirname(urdf_path)

            for link in root.findall('link'):
                for tag in ['visual', 'collision']:
                    elements = list(link.findall(tag))
                    for el in elements:
                        mesh = el.find('.//mesh')
                        if mesh is not None:
                            mesh_file = mesh.get('filename')
                            if mesh_file:
                                abs_path = os.path.normpath(os.path.join(urdf_dir, mesh_file))

                                is_missing = not os.path.exists(abs_path)
                                is_empty_or_corrupt = False
                                if not is_missing:
                                    is_empty_or_corrupt = os.path.getsize(abs_path) < 500

                                if is_missing or is_empty_or_corrupt:
                                    missing_name = os.path.basename(mesh_file)
                                    reason = "物理丢失" if is_missing else "空壳损坏文件"

                                    msg = f"[自愈修复] 切除崩溃源 ({reason}): {missing_name} -> 已安全移除其 <{tag}> 节点" if self.lang == 'zh' else \
                                          f"[Auto-Heal] Removed crash source ({reason}): {missing_name} -> <{tag}> node deleted"
                                    self.log(msg)

                                    link.remove(el)
                                    healed = True

            if healed:
                tree.write(urdf_path, encoding='utf-8', xml_declaration=True)
                msg_done = "[自愈修复] URDF 中的致命幽灵网格已全部剿灭！" if self.lang == 'zh' else \
                           "[Auto-Heal] All fatal ghost meshes cleared from URDF!"
                self.log(msg_done)
        except Exception as e:
            err_msg = f"[自愈模块错误] {e}" if self.lang == 'zh' else f"[Auto-Heal Error] {e}"
            self.log(err_msg)

        parent_dir = os.path.dirname(target_dir)
        new_target_dir = os.path.join(parent_dir, new_name)

        if target_dir != new_target_dir:
            try:
                if not os.path.exists(new_target_dir):
                    os.rename(target_dir, new_target_dir)
                    self.dir_input.setText(new_target_dir)
                    self.log(texts['clean_root_rename'].format(os.path.basename(target_dir), new_name))
                else:
                    self.log(texts['chk_err'].format(f"Cannot rename root directory, {new_name} already exists."))
            except Exception as e:
                self.log(texts['chk_err'].format(f"Root rename failed: {e}"))

        self.log("="*50 + "\n" + texts['clean_complete'])

    def run_check(self):
        if not self.validate_inputs(): return
        texts = self.t[self.lang]
        target_dir = self.dir_input.text().strip()

        self.log("\n" + "="*50)
        self.log(texts['log_check_start'])
        self.log("="*50)

        urdf_files = [os.path.join(r, f) for r, d, files in os.walk(target_dir) for f in files if f.endswith('.urdf')]
        if not urdf_files: 
            self.log(texts['chk_no_urdf'])
            return

        urdf_path = urdf_files[0]
        self.log(texts['chk_analyzing'].format(os.path.relpath(urdf_path, target_dir)))

        try:
            joints = ET.parse(urdf_path).getroot().findall('joint')
            self.log(texts['chk_total'].format(len(joints)))

            joint_dict = {}
            for j in joints:
                joint_dict.setdefault(j.get('type'), []).append(j.get('name'))

            for j_type, names in joint_dict.items():
                self.log(texts['chk_type'].format(j_type.upper(), len(names)))
                if j_type == 'fixed':
                    self.log(texts['chk_warn_fixed'])
                for name in names: self.log(f"  - {name}")
                self.log("")

            suspect_keywords = ['wheel', 'gripper', 'finger', 'claw']
            found = False
            for j in joints:
                if any(suspect in j.get('name').lower() for suspect in suspect_keywords):
                    if not found: self.log(texts['chk_suspect_head'])
                    found = True
                    self.log(texts['chk_suspect_found'].format(j.get('name'), j.get('type')))
            if not found:
                self.log(texts['chk_suspect_none'])

        except Exception as e:
            self.log(texts['chk_err'].format(e))
        self.log("="*50)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = URDFCleanerApp()
    ex.show()
    sys.exit(app.exec_())