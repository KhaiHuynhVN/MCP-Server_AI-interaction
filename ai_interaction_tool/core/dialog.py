# Main input dialog for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore, QtGui
import json
import os
import tempfile
import uuid
from pathlib import Path
from .config import ConfigManager
from ..ui.file_dialog import FileAttachDialog
from ..ui.image_attachment import ImageAttachmentWidget
from ..ui.styles import (
    get_main_stylesheet, 
    get_context_menu_stylesheet,
    get_file_container_stylesheet,
    get_file_placeholder_stylesheet,
    get_file_list_stylesheet,
    get_main_input_textedit_stylesheet
)
from ..utils.translations import get_translations, get_translation
from ..constants import (
    SHADOW_BLUR_RADIUS, SHADOW_OFFSET, SHADOW_OPACITY
)

class PasteImageTextEdit(QtWidgets.QTextEdit):
    """Custom QTextEdit that handles image paste events"""
    
    imagePasted = QtCore.pyqtSignal(str)  # Signal emitted when image is pasted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def insertFromMimeData(self, source):
        """Override to handle pasted images - save directly to database"""
        if source.hasImage():
            # Get image from clipboard
            image = source.imageData()
            if image and not image.isNull():
                # Convert QImage to QPixmap
                if isinstance(image, QtGui.QImage):
                    pixmap = QtGui.QPixmap.fromImage(image)
                elif isinstance(image, QtGui.QPixmap):
                    pixmap = image
                else:
                    super().insertFromMimeData(source)
                    return
                
                # Save directly to database directory
                try:
                    # Get project root directory
                    current_file = os.path.abspath(__file__)
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                    
                    # Create user_images directory
                    user_images_dir = os.path.join(project_root, "user_images")
                    os.makedirs(user_images_dir, exist_ok=True)
                    
                    # Generate unique filename directly in database
                    unique_id = str(uuid.uuid4())[:8]
                    db_filename = f"pasted_{unique_id}.png"
                    db_path = os.path.join(user_images_dir, db_filename)
                    
                    # Save directly to database - NO TEMP FILES
                    if pixmap.save(db_path, "PNG"):
                        # Emit signal with database path - UI will handle async processing
                        self.imagePasted.emit(db_path)
                        return
                        
                except Exception:
                    pass
        
        # For non-image content, use default behavior
        super().insertFromMimeData(source)

class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # Khởi tạo config manager
        self.config_manager = ConfigManager()
        
        # Set responsive sizing instead of fixed
        self.setMinimumSize(800, 700)  # Much larger minimum size for comfortable UX
        
        # Load saved window size or use default
        saved_width, saved_height = self.config_manager.get_window_size()
        self.resize(saved_width, saved_height)
        
        # Khởi tạo danh sách lưu đường dẫn file đính kèm
        self.attached_files = []
        
        # Initialize labels for compatibility (even though hidden)
        self.attached_files_label = QtWidgets.QLabel()  # Hidden label for compatibility
        self.attached_images_label = QtWidgets.QLabel()  # Hidden label for compatibility
        
        # Lưu workspace state để reuse - load từ config
        last_workspace = self.config_manager.get_last_workspace()
        if last_workspace and os.path.exists(last_workspace):
            self.current_workspace_path = last_workspace
            self.current_workspace_name = self.config_manager.get_last_workspace_name()
            # Load attached files từ config
            saved_files = self.config_manager.get_last_attached_files()
            if saved_files:
                self.attached_files = saved_files
        else:
            # Clear invalid workspace từ config
            self.current_workspace_path = None
            self.current_workspace_name = None
            if last_workspace:  # Có workspace path nhưng không tồn tại
                self.config_manager.set_last_workspace(None)
        
        # Thiết lập ngôn ngữ từ cấu hình
        self.current_language = self.config_manager.get_language()
        
        # Từ điển cho đa ngôn ngữ
        self.translations = get_translations()
        
        # Cập nhật tiêu đề cửa sổ theo ngôn ngữ đã chọn
        self.setWindowTitle(self.get_translation("window_title"))
        
        # Thiết lập stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Thêm chọn ngôn ngữ
        self._setup_language_selection()
        
        # Thêm tiêu đề và hướng dẫn
        self._setup_title_and_info()
        
        # Thêm input area
        self._setup_input_area()
        
        # Thêm horizontal attachment areas (files + images)
        self._setup_horizontal_attachments()
        
        # Thêm continue checkbox và warning
        self._setup_continue_options()
        
        # Thêm buttons
        self._setup_buttons()
        
        self.setLayout(self.layout)
        
        # Thiết lập focus cho input khi mở dialog
        self.input.setFocus()
        
        # Thiết lập drop shadow
        self._setup_shadow_effect()
        
        # Restore attached files UI nếu có
        self._restore_attached_files_ui()
        
        # Force refresh button styles để apply semantic colors
        self._refresh_button_styles()
        
        self.result_text = None
        self.result_continue = False
        self.result_ready = False
        
        # Setup resize timer for saving window size
        self.resize_timer = QtCore.QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.save_window_size)
        self.resize_timer.setInterval(500)  # Save 500ms after last resize
    
    def _setup_language_selection(self):
        """Thiết lập phần chọn ngôn ngữ"""
        language_layout = QtWidgets.QHBoxLayout()
        self.language_label = QtWidgets.QLabel(self.get_translation("language_label"), self)
        self.language_combo = QtWidgets.QComboBox(self)
        
        # Điều chỉnh thuộc tính cho QComboBox
        self.language_combo.setMaxVisibleItems(2)
        self.language_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.language_combo.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Tiếng Việt", "vi")
        
        # Thiết lập ngôn ngữ từ cấu hình đã lưu
        if self.current_language == "vi":
            self.language_combo.setCurrentIndex(1)
        else:
            self.language_combo.setCurrentIndex(0)
            
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        
        self.layout.addLayout(language_layout)
    
    def _setup_title_and_info(self):
        """Thiết lập thông tin hướng dẫn"""
        # Thêm hướng dẫn
        self.info_label = QtWidgets.QLabel(self.get_translation("info_label"), self)
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)
    
    def _setup_input_area(self):
        """Thiết lập khu vực nhập liệu"""
        # Sử dụng custom TextEdit để handle image paste
        self.input = PasteImageTextEdit(self)
        self.input.setPlaceholderText(self.get_translation("input_placeholder"))
        self.input.setMinimumHeight(200)  # Larger minimum for big window
        self.input.setMaximumHeight(400)  # Allow more text editing space
        
        # Apply beautiful input styling (without problematic scrollbar)
        self.input.setStyleSheet(get_main_input_textedit_stylesheet())
        
        # Connect image paste signal
        self.input.imagePasted.connect(self.handle_pasted_image)
        
        self.layout.addWidget(self.input)
    
    def _setup_horizontal_attachments(self):
        """Thiết lập khu vực đính kèm file và hình ảnh theo chiều ngang"""
        # Main horizontal container
        attachments_container = QtWidgets.QHBoxLayout()
        attachments_container.setSpacing(15)  # Space between file and image sections
        
        # === LEFT SIDE: File Attachments ===
        file_section = self._create_file_attachment_section()
        attachments_container.addWidget(file_section, 1)  # Stretch factor 1
        
        # === RIGHT SIDE: Image Attachments ===
        image_section = self._create_image_attachment_section()
        attachments_container.addWidget(image_section, 1)  # Stretch factor 1
        
        self.layout.addLayout(attachments_container)
    
    def _create_file_attachment_section(self):
        """Tạo section đính kèm file"""
        file_widget = QtWidgets.QWidget()
        file_layout = QtWidgets.QVBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(6)
        
        # All file buttons in one row
        file_buttons_layout = QtWidgets.QHBoxLayout()
        file_buttons_layout.setSpacing(8)
        
        # Attach button
        self.attach_btn = QtWidgets.QPushButton(self.get_translation("attach_btn"), self)
        self.attach_btn.setObjectName("attachBtn")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.attach_btn.setProperty("button-type", "info")
        
        # Clear buttons
        self.clear_selected_btn = QtWidgets.QPushButton(self.get_translation("clear_selected"), self)
        self.clear_selected_btn.setObjectName("clearSelectedBtn")
        self.clear_selected_btn.clicked.connect(self.clear_selected_files)
        self.clear_selected_btn.setEnabled(False)
        self.clear_selected_btn.setToolTip(self.get_translation("clear_selected_tooltip"))
        self.clear_selected_btn.setProperty("button-type", "warning")
        
        self.clear_all_btn = QtWidgets.QPushButton(self.get_translation("clear_all"), self)
        self.clear_all_btn.setObjectName("clearAllBtn")
        self.clear_all_btn.clicked.connect(self.clear_all_files)
        self.clear_all_btn.setEnabled(False)
        self.clear_all_btn.setToolTip(self.get_translation("clear_all_tooltip"))
        self.clear_all_btn.setProperty("button-type", "danger")
        
        # Add all buttons to same row
        file_buttons_layout.addWidget(self.attach_btn)
        file_buttons_layout.addWidget(self.clear_selected_btn)
        file_buttons_layout.addWidget(self.clear_all_btn)
        file_buttons_layout.addStretch()
        
        file_layout.addLayout(file_buttons_layout)
        
        
        # File list with styled container to match image section
        self.file_list_container = QtWidgets.QFrame()
        self.file_list_container.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.file_list_container.setStyleSheet(get_file_container_stylesheet())
        self.file_list_container.setVisible(True)  # Always show like image container
        self.file_list_container.setFixedHeight(300)  # Large height for many file items
        
        # Container layout
        file_container_layout = QtWidgets.QVBoxLayout(self.file_list_container)
        file_container_layout.setContentsMargins(2, 2, 2, 2)  # Match image container padding
        file_container_layout.setSpacing(0)  # No spacing for full fill
        
        # File placeholder (shown when no files)
        self.file_placeholder = QtWidgets.QLabel(self.get_translation("file_placeholder"))
        self.file_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.file_placeholder.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.file_placeholder.setStyleSheet(get_file_placeholder_stylesheet())
        
        # File list inside container
        self.file_list = QtWidgets.QListWidget()
        self.file_list.setVisible(False)  # Hidden by default, show when files added
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.file_list.setToolTip(self.get_translation("file_list_tooltip"))
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemSelectionChanged.connect(self.update_clear_buttons_state)
        self.file_list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # Apply dark theme styling
        self.file_list.setStyleSheet(get_file_list_stylesheet())
        
        # Add both to container layout directly - they will fill available space
        file_container_layout.addWidget(self.file_placeholder)
        file_container_layout.addWidget(self.file_list)
        
        file_layout.addWidget(self.file_list_container)
        
        return file_widget
    
    def _create_image_attachment_section(self):
        """Tạo section đính kèm hình ảnh - sử dụng component riêng"""
        # Sử dụng ImageAttachmentWidget component
        self.image_attachment_widget = ImageAttachmentWidget(self, self.current_language, self.translations, self.config_manager)
        
        # Reference các thành phần cần thiết từ component
        self.attach_image_btn = self.image_attachment_widget.attach_image_btn
        self.clear_images_btn = self.image_attachment_widget.clear_images_btn
        self.drag_drop_widget = self.image_attachment_widget.drag_drop_widget
        self.image_scroll_area = self.image_attachment_widget.image_scroll_area
        self.image_scroll_widget = self.image_attachment_widget.image_scroll_widget
        self.image_placeholder = self.image_attachment_widget.image_placeholder
        
        return self.image_attachment_widget

    def handle_pasted_image(self, db_image_path):
        """Handle image pasted into input area - use async processing like existing system"""
        # Use async processing pattern like existing image attachment system
        QtCore.QTimer.singleShot(0, lambda: self._process_pasted_image(db_image_path))
    
    def _process_pasted_image(self, db_image_path):
        """Process pasted image asynchronously"""
        try:
            # Use the image attachment widget to add the pasted image
            if hasattr(self, 'image_attachment_widget'):
                # Image is already in database, just add to UI
                if os.path.exists(db_image_path) and "user_images" in db_image_path:
                    # Convert to base64 from database
                    base64_data = self.image_attachment_widget.image_to_base64(db_image_path)
                    if base64_data:
                        # Add directly to attached_images
                        # SECURITY: Only store database-relative information
                        image_info = {
                            "path": db_image_path,
                            "filename": Path(db_image_path).name,
                            "base64_data": base64_data,
                            "media_type": "image/png",
                            "source_type": "pasted",
                            "db_filename": Path(db_image_path).name,
                            "relative_db_path": os.path.basename(db_image_path)  # Only filename
                        }
                        
                        self.image_attachment_widget.attached_images.append(image_info)
                        self.image_attachment_widget.add_image_preview(db_image_path)
                        
                        # Use async UI update like existing system
                        QtCore.QTimer.singleShot(0, lambda: self.image_attachment_widget.update_image_ui(auto_scroll=True))
                    
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, 
                self.get_translation("paste_error_title"), 
                self.get_translation("paste_error_message").format(error=str(e))
            )

    def _old_setup_file_attachment(self):
        """Thiết lập khu vực đính kèm file"""
        # Row 1: Attach button và label
        attach_layout = QtWidgets.QHBoxLayout()
        
        self.attach_btn = QtWidgets.QPushButton(self.get_translation("attach_btn"), self)
        self.attach_btn.setObjectName("attachBtn")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.attach_btn.setProperty("button-type", "info")
        
        
        attach_layout.addWidget(self.attach_btn)
        attach_layout.addStretch()
        
        self.layout.addLayout(attach_layout)
        
        # Row 2: Clear buttons (chỉ hiện khi có files)
        clear_layout = QtWidgets.QHBoxLayout()
        
        self.clear_selected_btn = QtWidgets.QPushButton(self.get_translation("clear_selected"), self)
        self.clear_selected_btn.setObjectName("clearSelectedBtn")
        self.clear_selected_btn.clicked.connect(self.clear_selected_files)
        self.clear_selected_btn.setEnabled(False)  # Always visible, but disabled by default
        self.clear_selected_btn.setToolTip(self.get_translation("clear_selected_tooltip"))
        self.clear_selected_btn.setProperty("button-type", "warning")
        
        self.clear_all_btn = QtWidgets.QPushButton(self.get_translation("clear_all"), self)
        self.clear_all_btn.setObjectName("clearAllBtn")
        self.clear_all_btn.clicked.connect(self.clear_all_files)
        self.clear_all_btn.setEnabled(False)  # Always visible, but disabled by default
        self.clear_all_btn.setToolTip(self.get_translation("clear_all_tooltip"))
        self.clear_all_btn.setProperty("button-type", "danger")
        
        clear_layout.addWidget(self.clear_selected_btn)
        clear_layout.addWidget(self.clear_all_btn)
        clear_layout.addStretch()
        
        self.layout.addLayout(clear_layout)
        
        # Danh sách file đính kèm - enable multi-select
        self.file_list = QtWidgets.QListWidget(self)
        self.file_list.setMaximumHeight(300)  # Much more space for files in large window
        self.file_list.setMinimumHeight(120)  # Larger minimum when visible
        self.file_list.setVisible(False)
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # Multi-select
        self.file_list.setToolTip(self.get_translation("file_list_tooltip"))
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemSelectionChanged.connect(self.update_clear_buttons_state)
        self.layout.addWidget(self.file_list)

    
    def _setup_continue_options(self):
        """Thiết lập các tùy chọn tiếp tục cuộc trò chuyện"""
        # Thêm checkbox tiếp tục trò chuyện
        continue_default = self.config_manager.get('ui_preferences.continue_chat_default', True)
        self.continue_checkbox = QtWidgets.QCheckBox(self.get_translation("continue_checkbox"), self)
        self.continue_checkbox.setChecked(continue_default)
        self.continue_checkbox.setToolTip("Khi chọn, Agent sẽ tự động hiển thị lại hộp thoại này sau khi trả lời")
        self.layout.addWidget(self.continue_checkbox)
        
        # Thêm auto keep-alive checkbox và timer
        auto_keepalive_default = self.config_manager.get('ui_preferences.auto_keepalive_default', False)
        self.auto_keepalive_checkbox = QtWidgets.QCheckBox(self.get_translation("auto_keepalive_checkbox"), self)
        self.auto_keepalive_checkbox.setChecked(auto_keepalive_default)
        self.auto_keepalive_checkbox.setToolTip("Tự động gửi tin nhắn duy trì kênh chat sau 15 phút để tránh timeout")
        self.layout.addWidget(self.auto_keepalive_checkbox)
        
        # Timer label
        self.timer_label = QtWidgets.QLabel(self.get_translation("auto_keepalive_timer").format(minutes=15, seconds=0), self)
        self.timer_label.setStyleSheet("color: #f9e2af; font-weight: bold;")
        self.layout.addWidget(self.timer_label)
        
        # Setup countdown timer
        self.setup_keepalive_timer()
        
        # Thêm nhãn cảnh báo về quy tắc gọi lại
        self.warning_label = QtWidgets.QLabel(
            self.get_translation("warning_label"), 
            self
        )
        self.warning_label.setObjectName("warningLabel")
        self.warning_label.setWordWrap(True)
        self.layout.addWidget(self.warning_label)
    
    def _setup_buttons(self):
        """Thiết lập các nút điều khiển"""
        # Tạo layout ngang cho các nút
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.submit_btn = QtWidgets.QPushButton(self.get_translation("submit_btn"), self)
        self.submit_btn.clicked.connect(self.submit_text)
        self.submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.submit_btn.setToolTip("Gửi tin nhắn (Ctrl+Enter)")
        self.submit_btn.setProperty("button-type", "success")
        
        self.close_btn = QtWidgets.QPushButton(self.get_translation("close_btn"), self)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.close_btn.setToolTip("Đóng hộp thoại và kết thúc cuộc trò chuyện")
        
        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(button_layout)
    
    def _setup_shadow_effect(self):
        """Thiết lập hiệu ứng đổ bóng"""
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(SHADOW_BLUR_RADIUS)
        shadow.setColor(QtGui.QColor(0, 0, 0, SHADOW_OPACITY))
        shadow.setOffset(*SHADOW_OFFSET)
        self.setGraphicsEffect(shadow)
    
    def _restore_attached_files_ui(self):
        """Restore UI cho attached files từ config"""
        if not self.attached_files:
            return
        
        # Clear list trước
        self.file_list.clear()
        
        # Rebuild UI từ attached files
        for item_info in self.attached_files:
            relative_path = item_info.get("relative_path", "")
            item_type = item_info.get("type", "unknown").upper()
            
            display_name = f"[{item_type}] {relative_path}"
            list_item = QtWidgets.QListWidgetItem(display_name)
            list_item.setToolTip(f"Full relative path: {relative_path}\nTip: Hold Ctrl+Click to select multiple items")
            self.file_list.addItem(list_item)
        
        # Hiển thị UI elements
        if self.attached_files:
            self.file_list.setVisible(True)
            self.file_placeholder.setVisible(False)
        
        # Update button states regardless
        self.update_clear_buttons_state()
    
    def get_translation(self, key):
        """
        Lấy bản dịch cho khóa ngôn ngữ dựa trên ngôn ngữ hiện tại
        """
        return get_translation(self.current_language, key)
    
    def change_language(self, index):
        """
        Thay đổi ngôn ngữ hiện tại và cập nhật giao diện
        """
        self.current_language = self.language_combo.itemData(index)
        
        # Lưu cấu hình khi thay đổi ngôn ngữ
        self.config_manager.set_language(self.current_language)
        
        # Cập nhật tiêu đề cửa sổ
        self.setWindowTitle(self.get_translation("window_title"))
        
        # Cập nhật các nhãn
        self.info_label.setText(self.get_translation("info_label"))
        self.language_label.setText(self.get_translation("language_label"))

        self.continue_checkbox.setText(self.get_translation("continue_checkbox"))
        self.auto_keepalive_checkbox.setText(self.get_translation("auto_keepalive_checkbox"))
        # No thinking UI to update
        self.warning_label.setText(self.get_translation("warning_label"))
        
        # Cập nhật các nút
        self.attach_btn.setText(self.get_translation("attach_btn"))
        self.submit_btn.setText(self.get_translation("submit_btn"))
        self.close_btn.setText(self.get_translation("close_btn"))
        self.clear_selected_btn.setText(self.get_translation("clear_selected"))
        self.clear_all_btn.setText(self.get_translation("clear_all"))
        
        # Cập nhật image component language
        if hasattr(self, 'image_attachment_widget'):
            self.image_attachment_widget.set_language(self.current_language)
        
        # Cập nhật tooltips
        self.clear_selected_btn.setToolTip(self.get_translation("clear_selected_tooltip"))
        self.clear_all_btn.setToolTip(self.get_translation("clear_all_tooltip"))
        self.file_list.setToolTip(self.get_translation("file_list_tooltip"))
        
        # Refresh tooltips cho tất cả items trong file list
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item and len(self.attached_files) > i:
                relative_path = self.attached_files[i]["relative_path"]
                item.setToolTip(self.get_translation("file_item_tooltip").format(path=relative_path))
        
        # Cập nhật placeholder
        self.input.setPlaceholderText(self.get_translation("input_placeholder"))
    
    def attach_file(self):
        """
        Mở hộp thoại chọn file/folder và thêm file được chọn vào danh sách đính kèm
        """
        # Sử dụng hộp thoại chọn file nâng cao với workspace support
        dialog = FileAttachDialog(self, self.current_language, self.translations)
        
        # Khôi phục workspace state nếu có
        if self.current_workspace_path:
            dialog.restore_workspace_state(self.current_workspace_path, self.attached_files)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_items = dialog.get_selected_files()
            workspace_name = dialog.get_workspace_path()
            
            # Lưu workspace state để lần sau sử dụng
            self.current_workspace_path = dialog.get_full_workspace_path()
            self.current_workspace_name = workspace_name
            
            # Persist workspace state vào config
            self.config_manager.set_last_workspace(self.current_workspace_path)
            self.config_manager.set_last_attached_files(self.attached_files)
            
            if not workspace_name:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "No Workspace Selected", 
                    "Please select a workspace directory!"
                )
                return

            # Sync lại toàn bộ attached_files từ dialog
            self._sync_attached_files_from_dialog(selected_items, workspace_name)
            
            # Save attached files state ngay sau khi sync từ dialog
            self.config_manager.set_last_attached_files(self.attached_files)
    
    def _sync_attached_files_from_dialog(self, selected_items, workspace_name):
        """Sync toàn bộ attached_files từ dialog về main UI"""
        # Clear UI hiện tại
        self.file_list.clear()
        self.attached_files.clear()
        
        # Rebuild từ selected_items trong dialog
        for relative_path in selected_items:
            item_name = os.path.basename(relative_path)
            item_type = self._determine_item_type(item_name, relative_path)
            
            item_info = {
                "relative_path": relative_path,
                "workspace_name": workspace_name,
                "name": item_name,
                "type": item_type
            }
            self.attached_files.append(item_info)
            
            display_name = f"[{item_type.upper()}] {relative_path}"
            list_item = QtWidgets.QListWidgetItem(display_name)
            list_item.setToolTip(self.get_translation("file_item_tooltip").format(path=relative_path))
            self.file_list.addItem(list_item)
        
        # Show/hide file list and placeholder
        if self.attached_files:
            self.file_list.setVisible(True)
            self.file_placeholder.setVisible(False)
        else:
            self.file_list.setVisible(False)
            self.file_placeholder.setVisible(True)
        
        # Always update button states (they're always visible now)
        self.update_clear_buttons_state()
    
    def update_clear_buttons_state(self):
        """Cập nhật trạng thái các nút clear dựa trên selection"""
        selected_items = self.file_list.selectedItems()
        has_selection = len(selected_items) > 0
        has_files = len(self.attached_files) > 0
        
        # Update Clear Selected button
        self.clear_selected_btn.setEnabled(has_selection)
        if has_selection:
            self.clear_selected_btn.setText(f"{self.get_translation('clear_selected')} ({len(selected_items)})")
            self.clear_selected_btn.setToolTip("Xóa các items đã chọn")
        else:
            self.clear_selected_btn.setText(self.get_translation("clear_selected"))
            self.clear_selected_btn.setToolTip("Chọn items để xóa")
        
        # Update Clear All button
        self.clear_all_btn.setEnabled(has_files)
        if has_files:
            self.clear_all_btn.setText(f"{self.get_translation('clear_all')} ({len(self.attached_files)})")
            self.clear_all_btn.setToolTip("Xóa tất cả items đã đính kèm")
        else:
            self.clear_all_btn.setText(self.get_translation("clear_all"))
            self.clear_all_btn.setToolTip("Không có items để xóa")
    
    def clear_selected_files(self):
        """Xóa các files đã chọn"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.information(
                self,
                self.get_translation("no_selection"), 
                self.get_translation("no_selection_message")
            )
            return
        
        # Xóa từ cuối để tránh thay đổi index
        rows_to_remove = []
        for item in selected_items:
            row = self.file_list.row(item)
            rows_to_remove.append(row)
        
        # Sort descending để xóa từ cuối
        rows_to_remove.sort(reverse=True)
        
        for row in rows_to_remove:
            self.file_list.takeItem(row)
            if row < len(self.attached_files):
                self.attached_files.pop(row)
        
        # Cập nhật trạng thái UI sau khi xóa
        self.update_clear_buttons_state()
        
        # Save state sau khi thay đổi
        self.config_manager.set_last_attached_files(self.attached_files)
        
        # Show placeholder if no files left
        if self.file_list.count() == 0:
            self.file_list.setVisible(False)
            self.file_placeholder.setVisible(True)
        
        # Update button states
        self.update_clear_buttons_state()
    
    def clear_all_files(self):
        """Xóa tất cả files đã đính kèm"""
        if not self.attached_files:
            return
            
        reply = QtWidgets.QMessageBox.question(
            self,
            self.get_translation("clear_all_files"),
            self.get_translation("clear_all_confirm").format(count=len(self.attached_files)),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Clear all elements
            self.file_list.clear()
            self.attached_files.clear()
            
            # Save empty state
            self.config_manager.set_last_attached_files(self.attached_files)
            
            # Hide UI elements that should be hidden
            self.file_list.setVisible(False)
            self.file_placeholder.setVisible(True)
            
            # Update button states để reset số trong ngoặc
            self.update_clear_buttons_state()
    
    def _determine_item_type(self, item_name, relative_path):
        """
        Xác định loại item (file hoặc folder) dựa trên tên và đường dẫn
        """
        # Danh sách các file đặc biệt không có extension nhưng vẫn là file
        known_files_without_ext = {
            'dockerfile', 'makefile', 'readme', 'license', 'changelog',
            'authors', 'contributors', 'copying', 'install', 'news',
            'procfile', 'rakefile', 'gemfile', 'vagrantfile'
        }
        
        # Tên file thường (lowercase để so sánh)
        lower_name = item_name.lower()
        
        # 1. Kiểm tra hidden files/folders (bắt đầu bằng dấu chấm)
        if item_name.startswith('.'):
            # Hidden files thường có extension (như .gitignore, .env)
            # Hidden folders thường không có (như .git, .vscode)
            if '.' in item_name[1:]:  # Có dấu chấm sau dấu chấm đầu
                return "file"
            else:
                return "folder"
        
        # 2. Kiểm tra các file đặc biệt không có extension
        if lower_name in known_files_without_ext:
            return "file"
        
        # 3. Kiểm tra có extension không
        if '.' in item_name and not item_name.endswith('.'):
            # Có extension -> likely file
            return "file"
        
        # 4. Kiểm tra pattern của folder common
        folder_patterns = [
            'src', 'lib', 'bin', 'test', 'tests', 'docs', 'doc',
            'build', 'dist', 'node_modules', 'vendor', 'assets',
            'static', 'public', 'components', 'utils', 'helpers',
            'config', 'configs', 'scripts', 'tools'
        ]
        
        if lower_name in folder_patterns:
            return "folder"
        
        # 5. Kiểm tra path depth - thường folder có nhiều level hơn
        path_parts = relative_path.split('/')
        if len(path_parts) > 2:  # workspace/folder/...
            # Nếu là item cuối cùng và không có extension -> có thể là folder
            if not ('.' in item_name and not item_name.endswith('.')):
                return "folder"
        
        # 6. Default: nếu không có extension thì coi là folder
        return "folder" if '.' not in item_name or item_name.endswith('.') else "file"
    
    def show_context_menu(self, position):
        """
        Hiển thị menu ngữ cảnh cho danh sách file đính kèm
        """
        menu = QtWidgets.QMenu()
        
        # Apply modern context menu styling
        menu.setStyleSheet(get_context_menu_stylesheet())
        
        remove_action = menu.addAction(self.get_translation("remove_file"))
        remove_all_action = menu.addAction(self.get_translation("clear_all"))
        
        current_item = self.file_list.itemAt(position)
        if current_item:
            action = menu.exec_(self.file_list.mapToGlobal(position))
            if action == remove_action:
                row = self.file_list.row(current_item)
                self.file_list.takeItem(row)
                self.attached_files.pop(row)
                
                # Save state sau khi remove
                self.config_manager.set_last_attached_files(self.attached_files)
                
                # Show placeholder if no files left
                if self.file_list.count() == 0:
                    self.file_list.setVisible(False)
                    self.file_placeholder.setVisible(True)
                
                # Update button states
                self.update_clear_buttons_state()
            
            elif action == remove_all_action:
                self.clear_all_files()

    def submit_text(self):
        """
        Phương thức xử lý khi người dùng nhấn nút Gửi.
        """
        text = self.input.toPlainText()
        attached_images = self.image_attachment_widget.get_attached_images() if hasattr(self, 'image_attachment_widget') else self.attached_images
        if text.strip() or self.attached_files or attached_images:
            result_dict = {
                "text": text,
                "language": self.current_language
            }
            
            # Thêm thông tin về file/folder đính kèm nếu có (chỉ metadata, không đọc content)
            if self.attached_files:
                result_dict["attached_files"] = []
                for item_info in self.attached_files:
                    try:
                        relative_path = item_info["relative_path"]
                        workspace_name = item_info["workspace_name"]
                        name = item_info["name"]
                        item_type = item_info["type"]
                        
                        # Chỉ thêm metadata, không đọc file content
                        result_dict["attached_files"].append({
                            "relative_path": relative_path,
                            "workspace_name": workspace_name,
                            "name": name,
                            "type": item_type
                        })
                    except Exception as e:
                        result_dict["attached_files"].append({
                            "relative_path": item_info.get("relative_path", "unknown"),
                            "workspace_name": item_info.get("workspace_name", ""),
                            "name": item_info.get("name", "unknown"),
                            "type": item_info.get("type", "unknown"),
                            "error": str(e)
                        })
            
            # Thêm thông tin về hình ảnh đính kèm nếu có
            attached_images = self.image_attachment_widget.get_attached_images() if hasattr(self, 'image_attachment_widget') else self.attached_images
            if attached_images:
                result_dict["attached_images"] = []
                for img_info in attached_images:
                    result_dict["attached_images"].append({
                        "base64_data": img_info["base64_data"],
                        "media_type": img_info["media_type"],
                        "filename": img_info["filename"]
                    })
            
            self.result_text = json.dumps(result_dict, ensure_ascii=False)
            self.result_continue = self.continue_checkbox.isChecked()
            self.result_ready = True
            
            # Lưu trạng thái checkbox vào config để lần sau sử dụng
            self.config_manager.set('ui_preferences.continue_chat_default', self.continue_checkbox.isChecked())
            # No thinking level to save - always "high" mode
            self.config_manager.save_config()
            
            # Save images to config before closing
            if hasattr(self, 'image_attachment_widget'):
                self.image_attachment_widget.save_images_to_config()
            
            self.input.clear()
            self.accept()
    
    # Cho phép gửi bằng phím Enter
    def resizeEvent(self, event):
        """Handle window resize events và save size với debounce"""
        super().resizeEvent(event)
        # Restart timer mỗi lần resize (debounce effect)
        self.resize_timer.start()
    
    def save_window_size(self):
        """Save current window size to config"""
        self.config_manager.set_window_size(self.width(), self.height())
    
    def closeEvent(self, event):
        """Save window size và images khi đóng dialog"""
        self.save_window_size()
        
        # Cleanup keep-alive timer để tránh memory leak
        if hasattr(self, 'keepalive_timer') and self.keepalive_timer.isActive():
            self.keepalive_timer.stop()
            self.keepalive_timer.deleteLater()
        
        # Save images to config if widget exists
        if hasattr(self, 'image_attachment_widget'):
            self.image_attachment_widget.save_images_to_config()
            
        # Save checkbox state for next session
        if hasattr(self, 'image_attachment_widget') and hasattr(self.image_attachment_widget, 'save_images_checkbox'):
            checkbox_state = self.image_attachment_widget.save_images_checkbox.isChecked()
            self.config_manager.set('ui_preferences.save_images_enabled', checkbox_state)
            
        super().closeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self.submit_text()
        else:
            super().keyPressEvent(event)

    def setup_keepalive_timer(self):
        """Setup countdown timer cho auto keep-alive feature"""
        # Timer properties
        self.keepalive_total_seconds = 15 * 60  # 15 minutes
        self.keepalive_remaining_seconds = self.keepalive_total_seconds
        
        # QTimer để countdown
        self.keepalive_timer = QtCore.QTimer(self)
        self.keepalive_timer.timeout.connect(self.update_keepalive_timer)
        self.keepalive_timer.start(1000)  # Update every second
        
        # Connect checkbox để save preference
        self.auto_keepalive_checkbox.toggled.connect(self.on_auto_keepalive_toggled)
        
    def update_keepalive_timer(self):
        """Update countdown timer và auto-submit khi hết thời gian"""
        if self.keepalive_remaining_seconds <= 0:
            # Auto submit nếu checkbox được check
            if self.auto_keepalive_checkbox.isChecked():
                self.auto_submit_keepalive()
                return
            else:
                # Reset timer nếu checkbox không được check
                self.keepalive_remaining_seconds = self.keepalive_total_seconds
        
        # Update display
        minutes = self.keepalive_remaining_seconds // 60
        seconds = self.keepalive_remaining_seconds % 60
        self.timer_label.setText(
            self.get_translation("auto_keepalive_timer").format(
                minutes=minutes, 
                seconds=f"{seconds:02d}"
            )
        )
        
        # Countdown
        self.keepalive_remaining_seconds -= 1
        
    def auto_submit_keepalive(self):
        """Auto submit tin nhắn keep-alive"""
        keepalive_message = self.get_translation("auto_keepalive_message")
        
        # Set message trong input field
        self.input.setPlainText(keepalive_message)
        
        # Force continue_chat = true cho keep-alive
        self.continue_checkbox.setChecked(True)
        
        # Submit
        self.submit_text()
        
    def on_auto_keepalive_toggled(self, checked):
        """Xử lý khi auto keep-alive checkbox được toggle"""
        # Save preference only - không reset timer
        self.config_manager.set('ui_preferences.auto_keepalive_default', checked)

    def _refresh_button_styles(self):
        """Force refresh button styles để apply semantic colors"""
        buttons_to_refresh = [
            self.submit_btn,
            self.attach_btn,
            self.clear_selected_btn,
            self.clear_all_btn,
            # Note: close_btn uses ID-based styling, không cần property refresh
        ]
        
        for button in buttons_to_refresh:
            # Force style refresh by unpolish then polish
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    @staticmethod
    def getText():
        dialog = InputDialog()
        result = dialog.exec_()
        if dialog.result_ready:
            return dialog.result_text, dialog.result_continue, True
        else:
            return "", False, False 