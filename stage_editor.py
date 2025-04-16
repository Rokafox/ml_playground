import tkinter as tk

CELL_SIZE = 20
GRID_SIZE = 30

class WallEditorReversedY:
    def __init__(self, root):
        self.root = root
        self.root.title("Wall Editor (Bottom Origin)")
        
        # Canvas 作成 (幅, 高さ = 30×20, 30×20)
        w = CELL_SIZE * GRID_SIZE
        h = CELL_SIZE * GRID_SIZE
        self.canvas = tk.Canvas(root, width=w, height=h)
        self.canvas.pack()

        # --- グリッド線を描画 (見た目は上が大きいが、論理的には下から y=0) ---
        # 通常: i=0 は一番上, i=30 は一番下、という順番ですが
        # 「見た目」は下が y=0 で上に向かって増えるように利用するため、
        # 描画そのものは上→下の順で線を引いておき、
        # クリック時や塗り時に座標変換を行います。
        for i in range(GRID_SIZE + 1):
            # 横線 (水平線) = y座標が i*CELL_SIZE (上から i 番目)
            self.canvas.create_line(
                0, i*CELL_SIZE, 
                w, i*CELL_SIZE
            )
            # 縦線 (垂直線) = x座標が i*CELL_SIZE
            self.canvas.create_line(
                i*CELL_SIZE, 0, 
                i*CELL_SIZE, h
            )

        # 壁セルを保持するための set
        # ※あくまで “左下(0,0)” 原点の座標系で記録
        self.wall_cells = set()

        # イベントバインド: 左クリック・左ドラッグ
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_left_click_drag)
        # イベントバインド: 右クリック・右ドラッグ (壁取り消し)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_click)

        # Export ボタン (押下すると壁座標一覧を出力)
        self.export_button = tk.Button(root, text="Export", command=self.export_walls)
        self.export_button.pack(pady=10)


    def canvas_to_grid(self, px, py):
        """
        Canvas 上のマウス座標(px, py)を、
        下を y=0 として上方向に y が増える座標系(gx, gy)に変換。
        
        Tkinter Canvas は「上が y=0 → 下に向かい y が増加」。
        しかし、ここでは「下が y=0 → 上に向かい y が増加」としたい。
        """
        # Canvas 全体の高さ
        H = GRID_SIZE * CELL_SIZE
        
        # 左下(0,0) → 上に y が増えるように:
        #   gx = px // CELL_SIZE
        #   gy = (H - 1 - py) // CELL_SIZE
        # ただし -1 はピクセル境界のズレを回避するために入れている。
        gx = px // CELL_SIZE
        gy = (H - 1 - py) // CELL_SIZE
        return (gx, gy)

    def grid_to_canvas_rect(self, gx, gy):
        """
        “下が y=0” 原点のマス (gx, gy) を、
        Canvas の描画用ピクセル座標に変換して、
        そのセルの左上, 右下の点 (x0, y0, x1, y1) を返す。
        """
        # Canvas 高さ
        H = GRID_SIZE * CELL_SIZE
        # まず左下が (gx * CELL_SIZE, gy * CELL_SIZE) になると考えるが
        # 実際の Canvas は上が 0 なので、y=0 の行は最下段 → Canvas y=(H - CELL_SIZE) 付近。
        # つまり “下原点 y=gy” → “Canvas 上では y_t = H - (gy+1)*CELL_SIZE”
        x0 = gx * CELL_SIZE
        y0 = H - (gy+1) * CELL_SIZE   # 上辺
        x1 = (gx + 1) * CELL_SIZE
        y1 = H - gy * CELL_SIZE       # 下辺
        return (x0, y0, x1, y1)

    def on_left_click(self, event):
        """左クリックで壁セルを追加。"""
        gx, gy = self.canvas_to_grid(event.x, event.y)
        self.toggle_wall(gx, gy, add=True)

    def on_left_click_drag(self, event):
        """左ドラッグでも壁セル追加。"""
        gx, gy = self.canvas_to_grid(event.x, event.y)
        self.toggle_wall(gx, gy, add=True)

    def on_right_click(self, event):
        """右クリックで壁セル削除。"""
        gx, gy = self.canvas_to_grid(event.x, event.y)
        self.toggle_wall(gx, gy, add=False)

    def toggle_wall(self, gx, gy, add=True):
        """(gx, gy) のセルを壁に追加 or 解除。"""
        # 範囲外の場合は無視
        if gx < 0 or gx >= GRID_SIZE or gy < 0 or gy >= GRID_SIZE:
            return
        
        if add:
            if (gx, gy) not in self.wall_cells:
                self.wall_cells.add((gx, gy))
                self.fill_cell(gx, gy, fill="black")
        else:
            if (gx, gy) in self.wall_cells:
                self.wall_cells.remove((gx, gy))
                # 塗りつぶしを白に戻す
                self.fill_cell(gx, gy, fill="white")
                # 枠線を再度引き直しておきたい場合は適宜
                x0, y0, x1, y1 = self.grid_to_canvas_rect(gx, gy)
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="gray")

    def fill_cell(self, gx, gy, fill="black"):
        """(gx, gy) のセルを指定色で塗りつぶす（下原点系→Canvas 変換）。"""
        x0, y0, x1, y1 = self.grid_to_canvas_rect(gx, gy)
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="gray")

    def export_walls(self):
        """壁セルをターミナルに出力 (Python の print)。"""
        wall_list = sorted(list(self.wall_cells), key=lambda w: (w[1], w[0]))
        print("Exported wall cells (bottom-origin):")
        print(wall_list)


def main():
    root = tk.Tk()
    app = WallEditorReversedY(root)
    root.mainloop()

if __name__ == "__main__":
    main()
