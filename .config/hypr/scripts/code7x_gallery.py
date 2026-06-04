import sys
import os
import requests
import hashlib
import subprocess
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QScrollArea, QGridLayout, QLabel, 
                             QFrame, QLineEdit, QComboBox, QCheckBox, QDialog, 
                             QSlider, QTabWidget, QGraphicsView, QGraphicsScene, 
                             QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QFont, QImage, QBrush, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QPointF, QRectF

# --- SYSTEM CONFIG ---
WALLPAPER_DIR = os.path.expanduser("~/Wallpapers/Cyberpunk")
CACHE_DIR = os.path.expanduser("~/.cache/code7x_gallery")
CONFIG_PATH = os.path.expanduser("~/.config/code7x_gallery_config.json")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(WALLPAPER_DIR, exist_ok=True)

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w') as f: json.dump(config, f)
    except: pass

COLOR_BG = "#0a0a12"
COLOR_SURFACE = "#16161e"
COLOR_ACCENT = "#00ffff" 
COLOR_ACCENT_DIM = "#004444"
COLOR_TEXT = "#ffffff"

class WallhavenFetcher(QThread):
    finished = pyqtSignal(list, int)
    def __init__(self, query, categories, purity, sorting, page=1, api_key=""):
        super().__init__()
        self.query = query; self.categories = categories; self.purity = purity
        self.sorting = sorting; self.page = page; self.api_key = api_key
    def run(self):
        try:
            url = f"https://wallhaven.cc/api/v1/search?q={self.query}&categories={self.categories}&purity={self.purity}&sorting={self.sorting}&page={self.page}"
            if self.api_key: url += f"&apikey={self.api_key}"
            response = requests.get(url, timeout=15).json()
            data = response.get('data', [])
            results = []
            for item in data:
                results.append({'thumb': item['thumbs']['original'], 'full': item['path'], 'id': f"wh_{item['id']}"})
            self.finished.emit(results, self.page)
        except: self.finished.emit([], self.page)

class ImageLoader(QThread):
    loaded = pyqtSignal(QPixmap)
    def __init__(self, url, target_path=None):
        super().__init__()
        self.url = url; self.target_path = target_path
    def run(self):
        try:
            if not self.target_path:
                img_id = hashlib.md5(self.url.encode()).hexdigest()
                self.target_path = os.path.join(CACHE_DIR, f"{img_id}_thumb.jpg")
            if not os.path.exists(self.target_path):
                r = requests.get(self.url, timeout=30)
                with open(self.target_path, 'wb') as f: f.write(r.content)
            pixmap = QPixmap(self.target_path)
            if not pixmap.isNull(): self.loaded.emit(pixmap)
        except Exception as e: print(f"Loader Error: {e}")

# --- CANVAS EDITOR CLASSES ---

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent):
        super().__init__(0, 0, 20, 20, parent)
        self.setBrush(QBrush(QColor(COLOR_ACCENT)))
        self.setPen(QPen(Qt.GlobalColor.white, 1))
        self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.parent_item = parent

    def mousePressEvent(self, event):
        event.accept()
        self.parent_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.start_pos = event.scenePos()
        self.start_scale = self.parent_item.scale()

    def mouseMoveEvent(self, event):
        event.accept()
        delta = event.scenePos() - self.start_pos
        orig_w = self.parent_item.src_rect.width()
        if orig_w > 0:
            new_scale = max(0.05, self.start_scale + (delta.x() / orig_w))
            self.parent_item.setScale(new_scale)

    def mouseReleaseEvent(self, event):
        event.accept()
        self.parent_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.scene().update()

class CropHandle(QGraphicsRectItem):
    def __init__(self, parent, edge):
        super().__init__(0, 0, 20, 20, parent)
        self.edge = edge
        self.parent_item = parent
        self.setBrush(QBrush(QColor("#ff00ff"))) # Magenta handles for cropping
        self.setPen(QPen(Qt.GlobalColor.white, 1))
        self.setCursor(Qt.CursorShape.SizeVerCursor if edge in ['top', 'bottom'] else Qt.CursorShape.SizeHorCursor)

    def mousePressEvent(self, event):
        event.accept()
        self.parent_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.start_pos = event.scenePos()
        self.start_src = QRectF(self.parent_item.src_rect)
        self.start_item_pos = QPointF(self.parent_item.pos())

    def mouseMoveEvent(self, event):
        event.accept()
        delta = event.scenePos() - self.start_pos
        scale = self.parent_item.scale()
        dx = delta.x() / scale
        dy = delta.y() / scale
        
        new_src = QRectF(self.start_src)
        new_pos = QPointF(self.start_item_pos)
        
        if self.edge == 'top':
            dy = min(new_src.height() - 50, dy)
            new_src.setTop(new_src.top() + dy)
            new_pos.setY(new_pos.y() + dy * scale)
        elif self.edge == 'bottom':
            dy = max(-new_src.height() + 50, dy)
            new_src.setBottom(new_src.bottom() + dy)
        elif self.edge == 'left':
            dx = min(new_src.width() - 50, dx)
            new_src.setLeft(new_src.left() + dx)
            new_pos.setX(new_pos.x() + dx * scale)
        elif self.edge == 'right':
            dx = max(-new_src.width() + 50, dx)
            new_src.setRight(new_src.right() + dx)
            
        self.parent_item.prepareGeometryChange()
        self.parent_item.src_rect = new_src
        self.parent_item.setPos(new_pos)
        self.parent_item.update_handles()

    def mouseReleaseEvent(self, event):
        event.accept()
        self.parent_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.scene().update()

class CroppableImageItem(QGraphicsItem):
    def __init__(self, pixmap):
        super().__init__()
        self.pixmap = pixmap
        self.src_rect = QRectF(pixmap.rect())
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.resize_handle = ResizeHandle(self)
        self.crop_top = CropHandle(self, 'top')
        self.crop_bottom = CropHandle(self, 'bottom')
        self.crop_left = CropHandle(self, 'left')
        self.crop_right = CropHandle(self, 'right')
        self.update_handles()
        
    def boundingRect(self):
        return QRectF(0, 0, self.src_rect.width(), self.src_rect.height())
        
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(self.boundingRect(), self.pixmap, self.src_rect)
        if self.isSelected():
            painter.setPen(QPen(QColor(COLOR_ACCENT), max(2.0, 2.0 / self.scale())))
            painter.drawRect(self.boundingRect())
            
    def update_handles(self):
        w = self.src_rect.width()
        h = self.src_rect.height()
        
        # Keep handles a reasonable size regardless of scale
        hw = max(20.0, 20.0 / self.scale())
        
        self.resize_handle.setRect(0, 0, hw, hw)
        self.resize_handle.setPos(w - hw/2, h - hw/2)
        
        for hd in [self.crop_top, self.crop_bottom, self.crop_left, self.crop_right]:
            hd.setRect(0, 0, hw, hw)
            
        self.crop_top.setPos(w/2 - hw/2, -hw/2)
        self.crop_bottom.setPos(w/2 - hw/2, h - hw/2)
        self.crop_left.setPos(-hw/2, h/2 - hw/2)
        self.crop_right.setPos(w - hw/2, h/2 - hw/2)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemScaleHasChanged:
            self.update_handles()
        return super().itemChange(change, value)

class CollageAssetLabel(QLabel):
    def __init__(self, data, parent_canvas):
        super().__init__()
        self.data = data; self.parent_canvas = parent_canvas
        self.setFixedSize(180, 120); self.setStyleSheet("border: 1px solid #333; background: #000;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.timer = QTimer(self); self.timer.timeout.connect(self.check); self.timer.start(1000); self.check()
    def check(self):
        p = self.data['full']
        if p.startswith('http'):
            img_id = hashlib.md5(p.encode()).hexdigest(); ext = p.split('.')[-1]
            p = os.path.join(WALLPAPER_DIR, f"code7x_{img_id}.{ext}")
        if os.path.exists(p):
            pix = QPixmap(p)
            if not pix.isNull():
                self.setPixmap(pix.scaled(180, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.timer.stop(); return
        img_id = hashlib.md5(self.data['full'].encode()).hexdigest(); tp = os.path.join(CACHE_DIR, f"{img_id}_thumb.jpg")
        if os.path.exists(tp):
            pix = QPixmap(tp)
            if not pix.isNull(): self.setPixmap(pix.scaled(180, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else: self.setText("LINKING...")
    def mousePressEvent(self, e): self.parent_canvas.add_to_canvas(self.data['full'])

class CollageCanvas(QDialog):
    def __init__(self, selected_images, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint); self.showFullScreen()
        self.setStyleSheet(f"background: {COLOR_BG}; color: {COLOR_TEXT};")
        mon = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"]))[0]
        self.mw, self.mh = mon['width'], mon['height']
        self.vw, self.vh = 3840, 2160
        layout = QHBoxLayout(self); canvas_col = QVBoxLayout()
        
        self.scene = QGraphicsScene(0, 0, self.vw, self.vh)
        self.scene.setBackgroundBrush(QBrush(QColor(0,0,0)))
        
        border_rect = QGraphicsRectItem(0, 0, self.vw, self.vh)
        border_rect.setPen(QPen(QColor(COLOR_ACCENT), 5))
        border_rect.setZValue(9999) # Keep border on top
        self.scene.addItem(border_rect)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background: #050505; border: none;")
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        canvas_col.addWidget(self.view)
        
        btns = QHBoxLayout(); done = QPushButton("FINALIZE_NEURAL_STITCH"); done.clicked.connect(self.finalize)
        done.setStyleSheet(f"background: {COLOR_ACCENT}; color: {COLOR_BG}; padding: 15px; font-weight: bold;")
        abort = QPushButton("ABORT"); abort.clicked.connect(self.reject); abort.setStyleSheet("background: #ff5555; color: white; padding: 15px;")
        btns.addWidget(done); btns.addWidget(abort); canvas_col.addLayout(btns); layout.addLayout(canvas_col, 4)
        
        side = QVBoxLayout(); side.addWidget(QLabel("ASSET_LIBRARY (CLICK TO ADD)"))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); widget = QWidget(); self.assets = QVBoxLayout(widget)
        for img in selected_images: self.assets.addWidget(CollageAssetLabel(img, self))
        self.assets.addStretch(); scroll.setWidget(widget); side.addWidget(scroll); layout.addLayout(side, 1)
        QTimer.singleShot(100, self.auto_fit)
        
    def auto_fit(self): self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def add_to_canvas(self, p):
        if p.startswith('http'):
            id = hashlib.md5(p.encode()).hexdigest(); ext = p.split('.')[-1]
            p = os.path.join(WALLPAPER_DIR, f"code7x_{id}.{ext}")
        if os.path.exists(p):
            pix = QPixmap(p)
            if not pix.isNull():
                item = CroppableImageItem(pix); item.setPos(self.vw/2 - pix.width()/2, self.vh/2 - pix.height()/2)
                self.scene.addItem(item)
    
    def finalize(self):
        self.scene.clearSelection()
        image = QImage(QSize(self.mw, self.mh), QImage.Format.Format_ARGB32); image.fill(Qt.GlobalColor.black)
        painter = QPainter(image); self.scene.render(painter, QRectF(image.rect()), QRectF(0, 0, self.vw, self.vh))
        painter.end(); out = os.path.join(CACHE_DIR, "canvas_result.png"); image.save(out); self.result_path = out; self.accept()

# --- SINGLE IMAGE SCROLL-CROP CLASSES ---

class FullScreenPreview(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint); self.showFullScreen()
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); self.label = QLabel(); self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: black;"); layout.addWidget(self.label); self.pixmap = pixmap
        QTimer.singleShot(50, self.load_pixmap)
    def load_pixmap(self): 
        if self.pixmap and hasattr(self.pixmap, 'isNull') and not self.pixmap.isNull(): 
            self.label.setPixmap(self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    def mousePressEvent(self, e): self.close()

class ScrollCropDialog(QDialog):
    def __init__(self, url, thumb, parent=None):
        super().__init__(parent); self.url = url; self.full_pix = None
        self.setWindowTitle("SCROLL_TO_CROP")
        self.setFixedSize(600, 750); self.setStyleSheet(f"background: {COLOR_BG}; border: 2px solid {COLOR_ACCENT};")
        layout = QVBoxLayout(self)
        
        # 16:9 Viewport
        box_w = 560
        box_h = int(box_w * 9 / 16) # 315
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(box_w + 20, box_h + 5) # Extra width for scrollbar
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setStyleSheet("border: 2px solid #00ffff; background: #000;")
        
        # Add Scaled Image to Scene
        scaled_thumb = thumb.scaledToWidth(box_w, Qt.TransformationMode.SmoothTransformation)
        self.scene.setSceneRect(0, 0, box_w, scaled_thumb.height())
        self.item = QGraphicsPixmapItem(scaled_thumb)
        self.scene.addItem(self.item)
        
        layout.addWidget(self.view, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.stat = QLabel("SCROLL_UP/DOWN_TO_SELECT_WALLPAPER_AREA")
        self.stat.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 12px; font-weight: bold;")
        self.stat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stat)
        
        preview_btn = QPushButton("FULL_QUALITY_PREVIEW")
        preview_btn.setStyleSheet(f"background: {COLOR_SURFACE}; color: {COLOR_ACCENT}; padding: 10px; border: 1px solid {COLOR_ACCENT};")
        preview_btn.clicked.connect(self.do_preview)
        layout.addWidget(preview_btn)
        
        apply = QPushButton("SET_WALLPAPER"); apply.clicked.connect(self.on_apply)
        apply.setStyleSheet(f"background: {COLOR_ACCENT}; color: {COLOR_BG}; padding: 15px; font-weight: bold;")
        layout.addWidget(apply)
        
        cancel = QPushButton("CANCEL"); cancel.clicked.connect(self.reject)
        cancel.setStyleSheet("background: #ff5555; color: white; padding: 10px;")
        layout.addWidget(cancel)

    def on_apply(self):
        max_scroll = self.view.verticalScrollBar().maximum()
        if max_scroll > 0:
            val = self.view.verticalScrollBar().value()
            self.offset_percent = (val / max_scroll) * 100
        else:
            self.offset_percent = 50
        self.accept()

    def do_preview(self):
        if self.full_pix: FullScreenPreview(self.full_pix, self).exec()
        else:
            self.stat.setText("LOADING_FULL_QUALITY..."); self.l = ImageLoader(self.url)
            self.l.loaded.connect(self.done_preview); self.l.start()
            
    def done_preview(self, pix): 
        self.full_pix = pix; self.stat.setText("READY"); FullScreenPreview(pix, self).exec()

# --- GALLERY CORE ---

class WallpaperCard(QFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent); self.data = data; self.sel = False; self.setFixedSize(220, 160)
        self.layout = QVBoxLayout(self); self.img = QLabel("SYNC..."); self.layout.addWidget(self.img)
        self.setCursor(Qt.CursorShape.PointingHandCursor); self.upd()
    def upd(self):
        b = f"2px solid {COLOR_ACCENT}" if self.sel else f"1px solid {COLOR_ACCENT_DIM}"
        self.setStyleSheet(f"WallpaperCard {{ background: {COLOR_SURFACE}; border: {b}; }}")
    def set_image(self, pix): self.img.setPixmap(pix.scaled(210, 150, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
    def mousePressEvent(self, e):
        app = self.window()
        if app.collage_mode: self.sel = not self.sel; self.upd(); app.handle_selection(self.data, self.sel)
        else: app.confirm_and_set(self.data['full'], self.img.pixmap())

class GalleryApp(QWidget):
    def __init__(self):
        super().__init__(); self.collage_mode = False; self.selected_images = []
        self.setWindowTitle("CODE7X NEURAL GALLERY"); self.resize(1100, 850)
        self.setStyleSheet(f"QWidget {{ background-color: {COLOR_BG}; color: {COLOR_TEXT}; font-family: 'JetBrainsMono Nerd Font'; }}")
        layout = QVBoxLayout(self); head = QHBoxLayout()
        logo = QLabel(" ▓▒░ CODE7X_GALLERY ░▒▓ "); logo.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 16px; font-weight: bold;")
        head.addWidget(logo); head.addStretch()
        self.col_btn = QPushButton("COLLAGE: OFF"); self.col_btn.setCheckable(True); self.col_btn.clicked.connect(self.toggle_col)
        head.addWidget(self.col_btn); head.addSpacing(20)
        self.api = QLineEdit(); self.api.setPlaceholderText("API_KEY"); self.api.setFixedWidth(150)
        self.config = load_config(); self.api.setText(self.config.get('api_key', ''))
        save = QPushButton("SAVE"); save.clicked.connect(self.save_key); head.addWidget(self.api); head.addWidget(save); layout.addLayout(head)
        self.tabs = QTabWidget(); self.online = QWidget(); self.init_on(); self.tabs.addTab(self.online, "SCAN")
        self.local = QWidget(); self.init_loc(); self.tabs.addTab(self.local, "ARCHIVE"); layout.addWidget(self.tabs)
        self.loaders = []; self.page = 1; self.loading = False; self.new_search(); self.tabs.currentChanged.connect(self.tab_ch)

    def toggle_col(self):
        self.collage_mode = self.col_btn.isChecked(); self.col_btn.setText("COLLAGE: ACTIVE" if self.collage_mode else "COLLAGE: OFF")
        if not self.collage_mode: self.selected_images = []; self.new_search(); self.load_loc()
    def handle_selection(self, d, s):
        if s:
            self.selected_images.append(d)
            if d['full'].startswith('http'):
                id = hashlib.md5(d['full'].encode()).hexdigest(); ext = d['full'].split('.')[-1]
                p = os.path.join(WALLPAPER_DIR, f"code7x_{id}.{ext}")
                if not os.path.exists(p): l = ImageLoader(d['full'], p); self.loaders.append(l); l.start()
        else: self.selected_images = [x for x in self.selected_images if x['full'] != d['full']]
        if len(self.selected_images) >= 2: self.scan_btn.setText(f"OPEN_CANVAS ({len(self.selected_images)})")
        else: self.scan_btn.setText("SCAN")
    def init_on(self):
        layout = QVBoxLayout(self.online); cp = QFrame(); cp_l = QVBoxLayout(cp)
        s_row = QHBoxLayout(); self.q = QLineEdit(""); self.scan_btn = QPushButton("SCAN")
        self.scan_btn.clicked.connect(self.on_scan); s_row.addWidget(self.q); s_row.addWidget(self.scan_btn); cp_l.addLayout(s_row)
        f_row = QHBoxLayout(); self.cats = [QCheckBox("Gen"), QCheckBox("Anime"), QCheckBox("Peep")]
        for c in self.cats: c.setChecked(True); f_row.addWidget(c)
        f_row.addSpacing(10); self.purs = [QCheckBox("SFW"), QCheckBox("Sketchy"), QCheckBox("NSFW")]
        self.purs[0].setChecked(True); [f_row.addWidget(p) for p in self.purs]
        self.sort = QComboBox(); self.sort.addItems(["toplist", "random", "hot"]); f_row.addWidget(self.sort)
        cp_l.addLayout(f_row); layout.addWidget(cp); self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.grid_w = QWidget(); self.grid = QGridLayout(self.grid_w); self.scroll.setWidget(self.grid_w); layout.addWidget(self.scroll)
        self.scroll.verticalScrollBar().valueChanged.connect(self.scrolled)
    def on_scan(self):
        if self.collage_mode and len(self.selected_images) >= 2:
            editor = CollageCanvas(self.selected_images, self)
            if editor.exec() == QDialog.DialogCode.Accepted: self.apply_wp(editor.result_path)
        else: self.new_search()
    def init_loc(self):
        l = QVBoxLayout(self.local); r = QPushButton("RESCAN"); r.clicked.connect(self.load_loc); l.addWidget(r)
        self.l_scroll = QScrollArea(); self.l_scroll.setWidgetResizable(True); self.l_grid_w = QWidget()
        self.l_grid = QGridLayout(self.l_grid_w); self.l_scroll.setWidget(self.l_grid_w); l.addWidget(self.l_scroll)
    def tab_ch(self, i): (i == 1 and self.load_loc())
    def load_loc(self):
        for i in reversed(range(self.l_grid.count())): (self.l_grid.itemAt(i).widget() and self.l_grid.itemAt(i).widget().setParent(None))
        files = [f for f in os.listdir(WALLPAPER_DIR) if f.lower().endswith(('.jpg', '.png', '.webp', '.jpeg'))]
        row, col = 0, 0
        for f in files:
            p = os.path.join(WALLPAPER_DIR, f); c = WallpaperCard({'full': p, 'thumb': p}, self.l_grid_w); self.l_grid.addWidget(c, row, col); c.set_image(QPixmap(p))
            col += 1; (col > 3 and (col := 0) or True) and (col == 0 and (row := row + 1))
    def save_key(self): self.config['api_key'] = self.api.text(); save_config(self.config)
    def new_search(self): self.page = 1; [self.grid.itemAt(i).widget().setParent(None) for i in reversed(range(self.grid.count())) if self.grid.itemAt(i).widget()]; self.start_fetch()
    def start_fetch(self):
        if self.loading: return
        self.loading = True; c = "".join(["1" if x.isChecked() else "0" for x in self.cats]); p = "".join(["1" if x.isChecked() else "0" for x in self.purs])
        self.f = WallhavenFetcher(self.q.text(), c, p, self.sort.currentText(), self.page, self.api.text()); self.f.finished.connect(self.on_f); self.f.start()
    def on_f(self, res, p):
        self.loading = False; r, c = self.grid.count() // 4, self.grid.count() % 4
        for i in res:
            card = WallpaperCard(i, self.grid_w); self.grid.addWidget(card, r, c); l = ImageLoader(i['thumb']); l.loaded.connect(card.set_image); l.start(); self.loaders.append(l)
            c += 1; (c > 3 and (c := 0) or True) and (c == 0 and (r := r + 1))
        self.page += 1
    def scrolled(self, v): (v > self.scroll.verticalScrollBar().maximum() - 200 and self.start_fetch())

    def confirm_and_set(self, src, thumb):
        dlg = ScrollCropDialog(src, thumb, self)
        if dlg.exec() == QDialog.DialogCode.Accepted: self.set_wp(src, dlg.offset_percent)

    def set_wp(self, src, offset):
        try:
            self.scan_btn.setText("PROCESSING...")
            id = hashlib.md5(src.encode()).hexdigest(); out = os.path.join(CACHE_DIR, f"crop_{id}.jpg")
            if src.startswith('http'):
                ext = src.split('.')[-1]; fin = os.path.join(WALLPAPER_DIR, f"code7x_{id}.{ext}")
                if not os.path.exists(fin): open(fin, 'wb').write(requests.get(src).content)
            else: fin = src
            mon = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"]))[0]; sw, sh = mon['width'], mon['height']
            img = QImage(fin); iw, ih = img.width(), img.height()
            if iw == 0: return
            rh = int(ih * (sw / iw)); exh = rh - sh
            if exh > 0: os.system(f"magick \"{fin}\" -resize {sw}x -crop {sw}x{sh}+0+{int(exh * offset / 100)} \"{out}\"")
            else: os.system(f"magick \"{fin}\" -resize {sw}x{sh}^ -gravity Center -extent {sw}x{sh} \"{out}\"")
            self.apply_wp(out)
        except Exception as e: print(e); self.scan_btn.setText("FAILED")

    def apply_wp(self, path):
        os.system(f"cp '{path}' ~/.cache/current_wallpaper.png"); os.system(f"awww img '{path}'")
        self.scan_btn.setText("SYNC_COMPLETE"); QTimer.singleShot(2000, lambda: self.scan_btn.setText("SCAN"))

if __name__ == "__main__":
    app = QApplication(sys.argv); ex = GalleryApp(); ex.show(); sys.exit(app.exec())
