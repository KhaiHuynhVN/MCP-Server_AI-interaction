# File tree components for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore, QtGui
import os
from ..constants import TREE_DEPTH_EXPANSION
from ..utils.file_utils import normalize_path_unicode, validate_file_path_in_workspace
from .styles import ModernTheme, FileTypeIcons

class FileSystemModel(QtWidgets.QFileSystemModel):
    """Mô hình hệ thống tệp tùy chỉnh cho cây thư mục"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_items = set()
        self._workspace_path = ""
        self.setReadOnly(True)
        self.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        # Ensure model shows directory hierarchy
        self.setRootPath("")  # Allow full filesystem access initially
    
    def setWorkspacePath(self, workspace_path):
        """Thiết lập workspace path"""
        self._workspace_path = normalize_path_unicode(workspace_path) if workspace_path else ""
    
    def isSelected(self, index):
        """Kiểm tra xem item có được chọn không"""
        if not index.isValid():
            return False
        
        item_path = normalize_path_unicode(self.filePath(index))
        return item_path in self._selected_items
    
    def setSelected(self, index, selected=True):
        """Đặt trạng thái chọn cho item"""
        if not index.isValid():
            return False
        
        item_path = normalize_path_unicode(self.filePath(index))
        
        if selected:
            self._selected_items.add(item_path)
        elif item_path in self._selected_items:
            self._selected_items.remove(item_path)
        
        return True
    
    def selectedItems(self):
        """Trả về danh sách các item đã chọn"""
        valid_items = []
        items_to_remove = []
        
        for item_path in self._selected_items:
            try:
                if os.path.exists(item_path):
                    valid_items.append(item_path)
                else:
                    items_to_remove.append(item_path)
            except Exception:
                items_to_remove.append(item_path)
        
        for item_path in items_to_remove:
            self._selected_items.discard(item_path)
        
        return valid_items
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        self._selected_items.clear()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Override data để hiển thị thông tin file"""
        if role == QtCore.Qt.DisplayRole:
            original_name = super().data(index, role)
            if original_name:
                normalized_name = normalize_path_unicode(str(original_name))
                return normalized_name
        
        return super().data(index, role)

class FileTreeView(QtWidgets.QTreeView):
    """Widget hiển thị cây thư mục với khả năng chọn nhiều file và folder"""
    itemSelected = QtCore.pyqtSignal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FileSystemModel(self)
        self.setModel(self.model)
        
        # Debug: Force show branches
        self.setRootIsDecorated(True)
        self.setExpandsOnDoubleClick(True)  # Allow double-click expansion
        
        # Apply minimal modern styling that preserves arrows
        modern_style = f"""
        QTreeView {{
            background-color: {ModernTheme.COLORS['surface0'].name()};
            color: {ModernTheme.COLORS['text'].name()};
            font-family: {ModernTheme.FONTS['family']};
            font-size: {ModernTheme.FONTS['default_size']}px;
            border: 1px solid {ModernTheme.COLORS['surface1'].name()};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QTreeView::item {{
            height: 24px;
            border: none;
            padding: 2px;
        }}
        
        QTreeView::item:hover {{
            background-color: {ModernTheme.COLORS['hover'].name()};
            border: 1px solid transparent;
            border-radius: 4px;
        }}
        
        QTreeView::item:selected {{
            background-color: {ModernTheme.COLORS['selected'].name()};
            border: 1px solid {ModernTheme.COLORS['selected_border'].name()};
            border-radius: 4px;
        }}
        
        QTreeView::item:selected:hover {{
            background-color: {ModernTheme.COLORS['selected'].name()};
            border: 1px solid {ModernTheme.COLORS['selected_border'].name()};
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(modern_style)
        
        # Force application style to make arrows bright
        app = QtWidgets.QApplication.instance()
        if app:
            # Set fusion style which gives more control over colors
            app.setStyle('Fusion')
            
            # Set application palette for bright arrows
            app_palette = QtGui.QPalette()
            bright_color = QtGui.QColor(ModernTheme.COLORS['accent_blue'])
            
            # Set all arrow-related colors
            app_palette.setColor(QtGui.QPalette.WindowText, bright_color)
            app_palette.setColor(QtGui.QPalette.Text, bright_color) 
            app_palette.setColor(QtGui.QPalette.ButtonText, bright_color)
            app_palette.setColor(QtGui.QPalette.Mid, bright_color)
            app_palette.setColor(QtGui.QPalette.Dark, bright_color)
            
            # Background colors
            app_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(ModernTheme.COLORS['background']))
            app_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(ModernTheme.COLORS['surface0']))
            
            # Hover colors - arrows will change to this color on hover
            app_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(ModernTheme.COLORS['accent_green']))
            app_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(ModernTheme.COLORS['accent_yellow']))
            
            app.setPalette(app_palette)
        
        # Basic tree view settings to preserve expansion arrows
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(20)
        
        # Performance optimizations
        self.setAutoScroll(True)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        # Hide unnecessary columns (keep only filename)
        self.hideColumn(1)  # Size
        self.hideColumn(2)  # Type
        self.hideColumn(3)  # Date Modified
        
        self._workspace_path = ""
        
        # Re-enable custom delegate now that arrows work
        delegate = FileTreeDelegate(self)
        self.setItemDelegate(delegate)
        
        # Connect signals
        self.clicked.connect(self.onItemClicked)
        
        # Enable custom drawing
        self.setMouseTracking(True)
        
        # Setup header
        header = self.header()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(200)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setMinimumSectionSize(150)
        header.hide()  # Hide header but keep tree decoration
        
        # Enable smooth scrolling
        self.verticalScrollBar().setSingleStep(10)
    
    def setRootPath(self, path):
        """Thiết lập đường dẫn gốc cho cây thư mục"""
        if not path:
            return False
        
        try:
            normalized_path = normalize_path_unicode(path)
            
            if not os.path.exists(normalized_path):
                return False
            
            if not os.path.isdir(normalized_path):
                return False
            
            if not os.access(normalized_path, os.R_OK):
                return False
            
            self._workspace_path = normalized_path
            self.model.setWorkspacePath(normalized_path)
            
            index = self.model.setRootPath(normalized_path)
            self.setRootIndex(index)
            
            try:
                self.expandToDepth(min(TREE_DEPTH_EXPANSION, 2))
            except Exception:
                pass
            
            return True
            
        except Exception:
            return False
    

    
    def onItemClicked(self, index):
        """Xử lý khi một mục được click"""
        try:
            if not index.isValid():
                return
            
            item_path = normalize_path_unicode(self.model.filePath(index))
            is_dir = self.model.isDir(index)
            

            
            is_selected = self.model.isSelected(index)
            
            if self.model.setSelected(index, not is_selected):
                self.itemSelected.emit(item_path, not is_selected)
                # Force refresh toàn bộ view để đảm bảo highlight hiển thị đúng
                self.refreshView()
            
        except Exception as e:
            # print(f"Error in onItemClicked: {str(e)}", file=sys.stderr)
            pass  # Silently ignore to avoid breaking MCP stdio
    
    def getSelectedItems(self):
        """Lấy danh sách các item đã chọn"""
        return self.model.selectedItems()
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        try:
            self.model.clearSelection()
            self.viewport().update()
        except Exception as e:
            # print(f"Error clearing selection: {str(e)}", file=sys.stderr)
            pass  # Silently ignore to avoid breaking MCP stdio
    
    def refreshView(self):
        """Force refresh toàn bộ tree view"""
        try:
            self.viewport().update()
            self.repaint()
        except Exception as e:
            # print(f"Error refreshing view: {str(e)}", file=sys.stderr)
            pass  # Silently ignore to avoid breaking MCP stdio
    
    def deselectItem(self, item_path):
        """Bỏ chọn một item cụ thể"""
        try:
            if not item_path:
                return
            
            normalized_path = normalize_path_unicode(item_path)
            root_index = self.rootIndex()
            
            if self._deselectItemAtLevel(root_index, normalized_path):
                return
            
            self._deselectItemRecursive(root_index, normalized_path)
            
        except Exception as e:
            # print(f"Error deselecting item: {str(e)}", file=sys.stderr)
            pass  # Silently ignore to avoid breaking MCP stdio
    
    def _deselectItemAtLevel(self, parent_index, item_path):
        """Tìm và bỏ chọn item ở một level cụ thể"""
        try:
            for i in range(self.model.rowCount(parent_index)):
                index = self.model.index(i, 0, parent_index)
                if not index.isValid():
                    continue
                
                current_path = normalize_path_unicode(self.model.filePath(index))
                if current_path == item_path:
                    self.model.setSelected(index, False)
                    self.viewport().update()
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _deselectItemRecursive(self, parent_index, item_path, max_depth=10):
        """Tìm và bỏ chọn item một cách đệ quy"""
        if max_depth <= 0:
            return False
        
        try:
            for i in range(self.model.rowCount(parent_index)):
                index = self.model.index(i, 0, parent_index)
                if not index.isValid():
                    continue
                
                current_path = normalize_path_unicode(self.model.filePath(index))
                if current_path == item_path:
                    self.model.setSelected(index, False)
                    self.viewport().update()
                    return True
                
                if self.model.isDir(index) and self.model.hasChildren(index):
                    # ONLY expand if already expanded, don't auto-expand during deselect
                    if self.isExpanded(index):
                        if self._deselectItemRecursive(index, item_path, max_depth - 1):
                            return True
            
            return False
            
        except Exception:
            return False
    


    def keyPressEvent(self, event):
        """Override key press để xử lý an toàn"""
        try:
            if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_F2]:
                return
            
            super().keyPressEvent(event)
            
        except Exception:
            pass

class FileTreeDelegate(QtWidgets.QStyledItemDelegate):
    """Modern delegate cho file tree với icon và styling đẹp"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = ModernTheme()
        self.file_icons = FileTypeIcons()
    
    def paint(self, painter, option, index):
        """Modern paint với rounded corners và icons"""
        try:
            if not index.isValid():
                super().paint(painter, option, index)
                return
            
            model = index.model()
            is_selected = hasattr(model, 'isSelected') and model.isSelected(index)
            is_directory = model.isDir(index)
            file_name = model.data(index, QtCore.Qt.DisplayRole)
            
            # Setup painter
            painter.save()
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # Create rounded rect với modern spacing
            rect = QtCore.QRectF(option.rect)
            rect.adjust(self.theme.SPACING['small'], 2, -self.theme.SPACING['small'], -2)
            
            # Draw background với rounded corners
            if is_selected:
                # Selected state với gradient
                gradient = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
                selected_color = self.theme.COLORS['selected']
                gradient.setColorAt(0, QtGui.QColor(selected_color.red(), selected_color.green(), selected_color.blue(), 50))
                gradient.setColorAt(1, QtGui.QColor(selected_color.red(), selected_color.green(), selected_color.blue(), 30))
                
                painter.setBrush(QtGui.QBrush(gradient))
                painter.setPen(QtGui.QPen(self.theme.COLORS['selected_border'], 1.5))
                painter.drawRoundedRect(rect, self.theme.SPACING['border_radius'], self.theme.SPACING['border_radius'])
            elif option.state & QtWidgets.QStyle.State_MouseOver:
                # Hover state
                painter.setBrush(QtGui.QBrush(self.theme.COLORS['hover']))
                painter.setPen(QtGui.QPen(self.theme.COLORS['surface1'], 1))
                painter.drawRoundedRect(rect, self.theme.SPACING['border_radius'], self.theme.SPACING['border_radius'])
            
            # Setup text rect và icon rect với proper spacing
            icon_size = self.theme.SPACING['icon_size']
            checkmark_size = self.theme.SPACING['checkmark_size']
            
            text_rect = option.rect.adjusted(40, 0, -35, 0)  # Space for icon and checkmark
            icon_rect = QtCore.QRect(option.rect.left() + 12, 
                                   option.rect.top() + (option.rect.height() - icon_size) // 2, 
                                   icon_size, icon_size)
            

            
            # Draw icon using FileTypeIcons
            icon_text = self.file_icons.get_icon(file_name, is_directory)
            icon_color = self.theme.COLORS['accent_yellow'] if is_directory else self.theme.COLORS['accent_green']
            
            # Draw icon with proper font
            icon_font = QtGui.QFont()
            icon_font.setPixelSize(self.theme.FONTS['icon_size'])
            painter.setFont(icon_font)
            painter.setPen(icon_color)
            painter.drawText(icon_rect, QtCore.Qt.AlignCenter, icon_text)
            
            # Draw text với modern typography
            text_color = self.theme.COLORS['text'] if not is_selected else self.theme.COLORS['text']
            font = QtGui.QFont(self.theme.FONTS['family'])
            font.setPixelSize(self.theme.FONTS['default_size'])
            if is_selected:
                font.setWeight(QtGui.QFont.Medium)
            
            painter.setFont(font)
            painter.setPen(text_color)
            
            # Truncate text if too long
            metrics = painter.fontMetrics()
            available_width = text_rect.width()
            elided_text = metrics.elidedText(str(file_name), QtCore.Qt.ElideRight, available_width)
            
            painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, elided_text)
            
            # Draw modern checkmark for selected items
            if is_selected:
                self._draw_modern_checkmark(painter, option.rect)
            
            painter.restore()
                
        except Exception as e:
            try:
                super().paint(painter, option, index)
            except Exception:
                pass
    

    
    def _draw_modern_checkmark(self, painter, rect):
        """Vẽ modern checkmark với style đẹp"""
        try:
            # Create circular background for checkmark
            check_size = self.theme.SPACING['checkmark_size']
            check_rect = QtCore.QRect(
                rect.right() - check_size - 8, 
                rect.center().y() - check_size // 2, 
                check_size, check_size
            )
            
            painter.save()
            
            # Draw circular background
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setBrush(QtGui.QBrush(self.theme.COLORS['accent_blue']))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(check_rect)
            
            # Draw checkmark inside circle
            painter.setPen(QtGui.QPen(self.theme.COLORS['background'], 2.5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            
            # Checkmark coordinates within the circle
            center_x = check_rect.center().x()
            center_y = check_rect.center().y()
            
            # First stroke of checkmark (shorter)
            painter.drawLine(
                center_x - 4, center_y,
                center_x - 1, center_y + 3
            )
            # Second stroke of checkmark (longer)
            painter.drawLine(
                center_x - 1, center_y + 3,
                center_x + 4, center_y - 2
            )
            
            painter.restore()
            
        except Exception:
            pass
    
    def sizeHint(self, option, index):
        """Override size hint với modern spacing"""
        try:
            size = super().sizeHint(option, index)
            size.setHeight(max(size.height(), self.theme.SPACING['item_height']))
            return size
        except Exception:
            return QtCore.QSize(200, self.theme.SPACING['item_height']) 