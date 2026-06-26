import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import random

class DiffieHellmanInputUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DH密钥交换可视化演示｜随机大素数生成+交换流程可视化")
        self.root.geometry("1080x820")

        # DH 参数存储
        self.p = None
        self.g = None
        self.a = None
        self.A = None
        self.b = None
        self.B = None
        self.Ka = None
        self.Kb = None
        self.step = 0  # 0~4

        self.create_widgets()

    # 米勒-拉宾大素数检测（支持大数）
    def is_prime_mr(self, n, rounds=8):
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(rounds):
            a = random.randint(2, min(n - 2, 2**32))
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for __ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    # 随机生成指定位数素数
    def generate_big_prime(self, bit_len):
        while True:
            num = random.getrandbits(bit_len)
            num |= (1 << (bit_len - 1)) | 1
            if self.is_prime_mr(num):
                return num

    # 找合法生成元 g
    def find_generator(self, p):
        if p == 2:
            return 1
        phi = p - 1
        factors = set()
        temp = phi
        i = 2
        while i * i <= temp:
            if temp % i == 0:
                factors.add(i)
                while temp % i == 0:
                    temp //= i
            i += 1
        if temp > 1:
            factors.add(temp)
        for g_candidate in range(2, p):
            flag = True
            for q in factors:
                if pow(g_candidate, phi // q, p) == 1:
                    flag = False
                    break
            if flag:
                return g_candidate
        return 2

    def create_widgets(self):
        # 顶部标题
        tk.Label(self.root, text="Diffie-Hellman 密钥协商可视化演示", font=("SimHei", 18, "bold")).pack(pady=6)

        # ========== 1. 随机生成素数面板 ==========
        rand_frame = ttk.LabelFrame(self.root, text="随机大素数自动生成区")
        rand_frame.pack(fill="x", padx=12, pady=4)

        tk.Label(rand_frame, text="素数位数：").grid(row=0, column=0, padx=6, pady=4)
        self.bit_box = ttk.Combobox(rand_frame, width=10, state="readonly")
        self.bit_box["values"] = ("8位", "16位", "32位")
        self.bit_box.current(1)
        self.bit_box.grid(row=0, column=1, padx=6, pady=4)

        gen_btn = ttk.Button(rand_frame, text="一键生成 p & g", command=self.rand_pg)
        gen_btn.grid(row=0, column=2, padx=12, pady=4)
        tk.Label(rand_frame, text="生成后自动填入下方输入框，也可手动修改参数").grid(row=0, column=3, padx=6)

        # ========== 2. 手动输入参数区 ==========
        input_frame = ttk.LabelFrame(self.root, text="参数手动输入区（随机生成后可修改）")
        input_frame.pack(fill="x", padx=12, pady=4)

        # p g 行
        tk.Label(input_frame, text="公共素数 p：").grid(row=0, column=0, padx=5, pady=3, sticky="e")
        self.ent_p = ttk.Entry(input_frame, width=22)
        self.ent_p.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(input_frame, text="生成元 g：").grid(row=0, column=2, padx=5, pady=3, sticky="e")
        self.ent_g = ttk.Entry(input_frame, width=22)
        self.ent_g.grid(row=0, column=3, padx=5, pady=3)

        # a b 私钥行
        tk.Label(input_frame, text="Alice私钥 a：").grid(row=1, column=0, padx=5, pady=3, sticky="e")
        self.ent_a = ttk.Entry(input_frame, width=22)
        self.ent_a.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(input_frame, text="Bob私钥 b：").grid(row=1, column=2, padx=5, pady=3, sticky="e")
        self.ent_b = ttk.Entry(input_frame, width=22)
        self.ent_b.grid(row=1, column=3, padx=5, pady=3)

        # ========== 3. 密钥交换可视化面板（核心新增） ==========
        vis_frame = ttk.LabelFrame(self.root, text="公钥交换流程可视化面板")
        vis_frame.pack(fill="x", padx=12, pady=6)

        # Alice 模块
        alice_frame = ttk.LabelFrame(vis_frame, text="Alice 客户端")
        alice_frame.grid(row=0, column=0, padx=10, pady=4)
        self.vis_a_pri = tk.Label(alice_frame, text="Alice私钥 a：待计算", font=("Consolas",10))
        self.vis_a_pri.pack(anchor="w", padx=6, pady=2)
        self.vis_a_pub = tk.Label(alice_frame, text="Alice公钥 A：待计算", font=("Consolas",10, "bold"), fg="#0066cc")
        self.vis_a_pub.pack(anchor="w", padx=6, pady=2)
        self.vis_alice_send = tk.Label(alice_frame, text="→ 发送公钥A给Bob：未发送", fg="#cc3300")
        self.vis_alice_send.pack(anchor="w", padx=6, pady=2)
        self.vis_alice_k = tk.Label(alice_frame, text="Alice共享密钥K：未生成", font=("Consolas",11, "bold"), fg="#009933")
        self.vis_alice_k.pack(anchor="w", padx=6, pady=2)

        # 中间交换箭头
        tk.Label(vis_frame, text="⬅⬅ 公钥互通 ➡➡", font=("SimHei",14)).grid(row=0, column=1, padx=15)

        # Bob 模块
        bob_frame = ttk.LabelFrame(vis_frame, text="Bob 客户端")
        bob_frame.grid(row=0, column=2, padx=10, pady=4)
        self.vis_b_pri = tk.Label(bob_frame, text="Bob私钥 b：待计算", font=("Consolas",10))
        self.vis_b_pri.pack(anchor="w", padx=6, pady=2)
        self.vis_b_pub = tk.Label(bob_frame, text="Bob公钥 B：待计算", font=("Consolas",10, "bold"), fg="#0066cc")
        self.vis_b_pub.pack(anchor="w", padx=6, pady=2)
        self.vis_bob_send = tk.Label(bob_frame, text="→ 发送公钥B给Alice：未发送", fg="#cc3300")
        self.vis_bob_send.pack(anchor="w", padx=6, pady=2)
        self.vis_bob_k = tk.Label(bob_frame, text="Bob共享密钥K：未生成", font=("Consolas",11, "bold"), fg="#009933")
        self.vis_bob_k.pack(anchor="w", padx=6, pady=2)

        # 步骤提示
        self.step_label = tk.Label(self.root, text="步骤1：点击【一键生成p&g】或手动填写公共参数，再点下一步", font=("SimHei", 12, "bold"), fg="#222222")
        self.step_label.pack(pady=4)

        # 日志输出框
        self.log_box = scrolledtext.ScrolledText(self.root, width=130, height=16, font=("Consolas", 9))
        self.log_box.pack(padx=12, pady=5)

        # 底部按钮区
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=8)
        self.next_btn = ttk.Button(btn_frame, text="下一步", command=self.next_step, width=14)
        self.next_btn.grid(row=0, column=0, padx=12)
        reset_btn = ttk.Button(btn_frame, text="重置全部流程", command=self.reset_all, width=14)
        reset_btn.grid(row=0, column=1, padx=12)

    # 随机生成p g 填充输入框
    def rand_pg(self):
        bit_text = self.bit_box.get()
        bit_len = int(bit_text.replace("位",""))
        self.log(f"正在生成 {bit_len} 位大素数 p，请稍等...")
        p = self.generate_big_prime(bit_len)
        g = self.find_generator(p)
        self.ent_p.delete(0, tk.END)
        self.ent_p.insert(0, str(p))
        self.ent_g.delete(0, tk.END)
        self.ent_g.insert(0, str(g))
        self.log(f"✅ 随机生成完成：{bit_len}位素数 p={p}，对应生成元 g={g}\n")

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)
        self.root.update()

    def get_int(self, entry):
        txt = entry.get().strip()
        if not txt:
            messagebox.showerror("输入错误", "输入框不能为空！")
            return None
        try:
            return int(txt)
        except ValueError:
            messagebox.showerror("输入错误", "只能输入纯数字！")
            return None

    def next_step(self):
        if self.step == 0:
            # 步骤1 读取公共参数 p g
            p = self.get_int(self.ent_p)
            g = self.get_int(self.ent_g)
            if p is None or g is None:
                return
            if not self.is_prime_mr(p):
                messagebox.showerror("参数校验", f"{p} 不是合法素数！")
                return
            if g <= 1 or g >= p:
                messagebox.showerror("参数校验", f"生成元必须满足 1 < g < {p}")
                return
            self.p = p
            self.g = g
            self.log("===== 步骤1 公共参数确认 =====")
            self.log(f"公共大素数 p = {self.p}")
            self.log(f"生成元 g = {self.g}\n")
            self.step += 1
            self.step_label.config(text="步骤2：填写Alice私钥a，下一步计算Alice公钥A")

        elif self.step == 1:
            # 步骤2 Alice私钥&公钥A
            a = self.get_int(self.ent_a)
            if a is None:
                return
            if a <= 1 or a >= self.p:
                messagebox.showerror("参数校验", f"私钥a范围：1 < a < {self.p}")
                return
            self.a = a
            self.A = pow(self.g, self.a, self.p)
            self.log("===== 步骤2 Alice生成公私钥 =====")
            self.log(f"Alice本地私钥 a = {self.a}（保密不传输）")
            self.log(f"Alice公钥 A = g^a mod p = {self.A}\n")
            # 更新可视化面板 Alice区域
            self.vis_a_pri.config(text=f"Alice私钥 a：{self.a}")
            self.vis_a_pub.config(text=f"Alice公钥 A：{self.A}")
            self.step += 1
            self.step_label.config(text="步骤3：填写Bob私钥b，下一步计算Bob公钥B")

        elif self.step == 2:
            # 步骤3 Bob私钥&公钥B
            b = self.get_int(self.ent_b)
            if b is None:
                return
            if b <= 1 or b >= self.p:
                messagebox.showerror("参数校验", f"私钥b范围：1 < b < {self.p}")
                return
            self.b = b
            self.B = pow(self.g, self.b, self.p)
            self.log("===== 步骤3 Bob生成公私钥 =====")
            self.log(f"Bob本地私钥 b = {self.b}（保密不传输）")
            self.log(f"Bob公钥 B = g^b mod p = {self.B}\n")
            # 更新可视化 Bob区域
            self.vis_b_pri.config(text=f"Bob私钥 b：{self.b}")
            self.vis_b_pub.config(text=f"Bob公钥 B：{self.B}")
            self.step += 1
            self.step_label.config(text="步骤4：执行公钥双向交换，计算双方共享密钥")

        elif self.step == 3:
            # 步骤4 公钥交换 + 共同密钥计算
            self.log("===== 步骤4 公钥双向交换流程可视化 =====")
            # 可视化更新交换状态
            self.vis_alice_send.config(text=f"→ 发送公钥A={self.A} 给Bob ✅", fg="#009933")
            self.vis_bob_send.config(text=f"→ 发送公钥B={self.B} 给Alice ✅", fg="#009933")
            self.log(f"1. Alice 将公钥 A={self.A} 明文发送给 Bob")
            self.log(f"2. Bob 将公钥 B={self.B} 明文发送给 Alice\n")

            # 双方计算共享密钥
            self.Ka = pow(self.B, self.a, self.p)
            self.log(f"Alice 计算共享密钥 K = B^a mod p = {self.B}^{self.a} mod {self.p} = {self.Ka}")
            self.Kb = pow(self.A, self.b, self.p)
            self.log(f"Bob 计算共享密钥 K = A^b mod p = {self.A}^{self.b} mod {self.p} = {self.Kb}\n")

            # 可视化展示最终密钥
            self.vis_alice_k.config(text=f"Alice共享密钥K：{self.Ka}")
            self.vis_bob_k.config(text=f"Bob共享密钥K：{self.Kb}")

            if self.Ka == self.Kb:
                self.log(f"✅ 协商成功！双方得到完全一致的共享密钥 K = {self.Ka}")
                self.log("核心数学原理：g^(ab) mod p = (g^a)^b mod p = (g^b)^a mod p")
            else:
                self.log("❌ 密钥不匹配（输入参数异常）")

            self.step += 1
            self.step_label.config(text="流程全部结束，点击【重置全部流程】重新演示")
            self.next_btn.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("提示", "演示流程已走完，请重置后重新开始！")

    def reset_all(self):
        # 清空输入框
        self.ent_p.delete(0, tk.END)
        self.ent_g.delete(0, tk.END)
        self.ent_a.delete(0, tk.END)
        self.ent_b.delete(0, tk.END)
        # 清空日志
        self.log_box.delete(1.0, tk.END)
        # 重置所有DH变量
        self.p = self.g = self.a = self.A = self.b = self.B = self.Ka = self.Kb = None
        self.step = 0
        self.step_label.config(text="步骤1：点击【一键生成p&g】或手动填写公共参数，再点下一步")
        self.next_btn.config(state=tk.NORMAL)

        # 重置可视化面板文字
        self.vis_a_pri.config(text="Alice私钥 a：待计算")
        self.vis_a_pub.config(text="Alice公钥 A：待计算")
        self.vis_alice_send.config(text="→ 发送公钥A给Bob：未发送", fg="#cc3300")
        self.vis_alice_k.config(text="Alice共享密钥K：未生成")

        self.vis_b_pri.config(text="Bob私钥 b：待计算")
        self.vis_b_pub.config(text="Bob公钥 B：待计算")
        self.vis_bob_send.config(text="→ 发送公钥B给Alice：未发送", fg="#cc3300")
        self.vis_bob_k.config(text="Bob共享密钥K：未生成")

        self.log("已完整重置，可随机生成大素数或手动输入参数重新开始演示\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiffieHellmanInputUI(root)
    root.mainloop()