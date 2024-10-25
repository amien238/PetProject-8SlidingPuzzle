import tkinter as tk
import random
import copy
from queue import PriorityQueue
from tkinter import messagebox
from PIL import Image, ImageTk  # Thư viện PIL để xử lý hình ảnh


def is_goal(state, size):
    goal = [[(i * size + j + 1) % (size * size) for j in range(size)] for i in range(size)]
    return state == goal

# Hàm tính heuristic (hàm khoảng cách Manhattan)
def manhattan_distance(state, goal, size):
    dist = 0
    for i in range(size):
        for j in range(size):
            if state[i][j] != 0:
                x, y = divmod(goal.index(state[i][j]), size)
                dist += abs(x - i) + abs(y - j) 
    return dist

# Hàm kiểm tra tính chẵn lẻ của số đảo ngược để xác định trạng thái có thể giải được
def is_solvable(state, size):
    flat_state = [num for row in state for num in row if num != 0]
    inversions = 0

    for i in range(len(flat_state)):
        for j in range(i + 1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1

    if size % 2 == 1:  # Lưới kích thước lẻ (3x3, 5x5)
        return inversions % 2 == 0
    else:  # Lưới kích thước chẵn (8x8)
        zero_row = [i for i, row in enumerate(state) if 0 in row][0]
        return (inversions + zero_row) % 2 == 0

# Hàm tạo trạng thái có thể giải được bằng cách tráo từ trạng thái đích
def shuffle_solvable(size):
    state = [[(i * size + j + 1) % (size * size) for j in range(size)] for i in range(size)]
    flat_state = [num for row in state for num in row]
    zero_index = flat_state.index(0)
    
    for _ in range(1000):  # Thực hiện nhiều lần tráo ngẫu nhiên
        zero_row, zero_col = divmod(zero_index, size)
        moves = []
        if zero_row > 0: moves.append((-1, 0))  # Move up
        if zero_row < size - 1: moves.append((1, 0))  # Move down
        if zero_col > 0: moves.append((0, -1))  # Move left
        if zero_col < size - 1: moves.append((0, 1))  # Move right
        
        move = random.choice(moves)
        new_row, new_col = zero_row + move[0], zero_col + move[1]
        new_index = new_row * size + new_col
        
        flat_state[zero_index], flat_state[new_index] = flat_state[new_index], flat_state[zero_index]
        zero_index = new_index

    state = [flat_state[i:i + size] for i in range(0, len(flat_state), size)]
    
    if is_solvable(state, size):
        return state
    else:
        return shuffle_solvable(size)
    
def a_star_search(start, size):
    goal = [(i * size + j + 1) % (size * size) for i in range(size) for j in range(size)]
    frontier = PriorityQueue()
    frontier.put((manhattan_distance(start, goal, size), 0, start, []))
    visited = set()

    while not frontier.empty():
        _, cost, current, path = frontier.get()
        current_flat = tuple(item for row in current for item in row)

        if current_flat in visited:
            continue

        visited.add(current_flat)

        if is_goal(current, size):
            return path

        zero_pos = [(i, j) for i in range(size) for j in range(size) if current[i][j] == 0][0]
        x, y = zero_pos

        for dx, dy, action in [(-1, 0, 'Up'), (1, 0, 'Down'), (0, -1, 'Left'), (0, 1, 'Right')]:
            new_x, new_y = x + dx, y + dy

            if 0 <= new_x < size and 0 <= new_y < size:
                new_state = copy.deepcopy(current)
                new_state[x][y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[x][y]
                new_flat = tuple(item for row in new_state for item in row)

                if new_flat not in visited:
                    new_path = path + [action]
                    new_cost = cost + 1
                    priority = new_cost + manhattan_distance(new_state, goal, size)
                    frontier.put((priority, new_cost, new_state, new_path))

    return None

# Giao diện Tkinter với hình ảnh
class PuzzleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Sliding Puzzle Game")
        self.size = 3  # Mặc định là 3x3 (Easy)
        self.state = []
        self.buttons = []
        self.tiles = []  # Danh sách chứa các mảnh ghép (hình ảnh)
        self.image_path = "f01277f72d78aba26bc90f88af1101cc.jpg"  # Đường dẫn tới hình ảnh mà bạn muốn dùng
        self.original_image = None
        self.image_refs = []  # Danh sách để giữ các tham chiếu đến các mảnh hình ảnh

        self.create_widgets()

    # Hàm tạo các thành phần giao diện
    def create_widgets(self):
        # Lựa chọn cấp độ
        self.level_label = tk.Label(self.master, text="Chọn cấp độ:")
        self.level_label.grid(row=0, column=0, columnspan=3)

        self.level_var = tk.StringVar(value="Easy")
        self.level_menu = tk.OptionMenu(self.master, self.level_var, "Easy", "Medium", "Hard", command=self.select_level)
        self.level_menu.grid(row=1, column=0, columnspan=3)

        # Tạo lưới các nút
        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.grid(row=2, column=0, columnspan=3)
        self.create_grid()

        # Nút tráo trạng thái và giải đố
        self.shuffle_button = tk.Button(self.master, text="Shuffle", command=self.shuffle)
        self.shuffle_button.grid(row=3, column=0, columnspan=3, sticky="nsew")

        self.solve_button = tk.Button(self.master, text="Solve", command=self.solve)
        self.solve_button.grid(row=4, column=0, columnspan=3, sticky="nsew")

    # Hàm lựa chọn cấp độ và cập nhật kích thước lưới
    def select_level(self, choice):
        if choice == "Easy":
            self.size = 3
        elif choice == "Medium":
            self.size = 5
        else:
            self.size = 8
        self.create_grid()
        self.shuffle()

    # Hàm tạo lưới
    def create_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.load_image()  # Tải và cắt hình ảnh
        self.state = [[(i * self.size + j + 1) % (self.size * self.size) for j in range(self.size)] for i in range(self.size)]
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]

        for i in range(self.size):
            for j in range(self.size):
                button = tk.Button(self.grid_frame, image=self.tiles[i][j] if self.state[i][j] != 0 else "",
                                   height = 150 // self.size, width = 150 // self.size, 
                                   command=lambda i=i, j=j: self.move(i, j))
                button.grid(row=i, column=j)
                self.buttons[i][j] = button

    # Hàm tải và cắt hình ảnh thành các mảnh
    def load_image(self):
        self.original_image = Image.open(self.image_path)
        self.original_image = self.original_image.resize((150, 150))  # Resize ảnh gốc cho vừa với kích thước
        tile_width = self.original_image.width // self.size
        tile_height = self.original_image.height // self.size

        self.tiles = []
        self.image_refs = []  # Reset danh sách tham chiếu hình ảnh
        for i in range(self.size):
            row = []
            for j in range(self.size):
                # Cắt hình thành từng mảnh
                tile = self.original_image.crop((j * tile_width, i * tile_height,
                                                 (j + 1) * tile_width, (i + 1) * tile_height))
                tile_photo = ImageTk.PhotoImage(tile)
                row.append(tile_photo)
                self.image_refs.append(tile_photo)  # Giữ tham chiếu đến đối tượng hình ảnh
            self.tiles.append(row)

    # Hàm tráo trạng thái ngẫu nhiên
    def shuffle(self):
        self.state = shuffle_solvable(self.size)
        self.update_ui()

    # Hàm cập nhật giao diện
    def update_ui(self):
        for i in range(self.size):
            for j in range(self.size):
                self.buttons[i][j].config(image=self.tiles[i][j] if self.state[i][j] != 0 else "")

    # Hàm di chuyển ô
    def move(self, i, j):
        zero_pos = [(i, j) for i in range(self.size) for j in range(self.size) if self.state[i][j] == 0][0]
        x, y = zero_pos

        if abs(x - i) + abs(y - j) == 1:  # Chỉ cho phép di chuyển kề cạnh
            self.state[x][y], self.state[i][j] = self.state[i][j], self.state[x][y]
            self.update_ui()

    # Hàm máy giải đố
    def solve(self):
        solution = a_star_search(self.state, self.size)
        if solution:
            self.apply_solution(solution)
        else:
            messagebox.showinfo("Kết quả", "Không còn đường giải. Bạn đã thua!")
            self.shuffle()

    # Hàm áp dụng các bước giải từ thuật toán A*
    def apply_solution(self, solution):
        for step in solution:
            self.master.update()
            self.master.after(500)  # Tạm dừng 500ms giữa mỗi bước
            zero_pos = [(i, j) for i in range(self.size) for j in range(self.size) if self.state[i][j] == 0][0]
            x, y = zero_pos

            if step == 'Up':
                self.move(x - 1, y)
            elif step == 'Down':
                self.move(x + 1, y)
            elif step == 'Left':
                self.move(x, y - 1)
            elif step == 'Right':
                self.move(x, y + 1)

# Chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()
