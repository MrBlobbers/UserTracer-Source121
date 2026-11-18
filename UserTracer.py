import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import urllib.error
import urllib.request

TARGET_SITES = {
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "YouTube": "https://www.youtube.com/@{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Chess.com": "https://www.chess.com/member/{}",
    "Medium": "https://medium.com/@{}",
}


class UserTraceApp:

  def __init__(self, root):
    self.root = root
    self.root.title("UserTracer")
    self.root.geometry("750x600")
    self.root.minsize(650, 500)

    self.style = ttk.Style()
    self.style.theme_use("clam")

    header_frame = tk.Frame(root, bg="#1e293b", pady=15)
    header_frame.pack(fill=tk.X)

    title_label = tk.Label(
        header_frame,
        text="UserTracer",
        font=("Arial", 16, "bold"),
        fg="white",
        bg="#1e293b",
    )
    title_label.pack()

    input_frame = tk.Frame(root, padx=20, pady=15)
    input_frame.pack(fill=tk.X)

    tk.Label(
        input_frame, text="Target Username:", font=("Arial", 10, "bold")
    ).pack(side=tk.LEFT, padx=(0, 10))

    self.username_entry = ttk.Entry(input_frame, font=("Arial", 11), width=30)
    self.username_entry.pack(side=tk.LEFT, padx=(0, 10))
    self.username_entry.bind("<Return>", lambda event: self.start_search())

    self.search_button = ttk.Button(
        input_frame, text="Run Search", command=self.start_search
    )
    self.search_button.pack(side=tk.LEFT)

    results_frame = tk.Frame(root, padx=20, pady=5)
    results_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        results_frame, text="Search Results Report:", font=("Arial", 10, "bold")
    ).pack(anchor=tk.W, pady=(0, 5))

    self.output_area = scrolledtext.ScrolledText(
        results_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg="#0f172a",
        fg="#f8fafc",
        insertbackground="white",
    )
    self.output_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    self.status_var = tk.StringVar(value="Status: Ready")
    status_bar = tk.Label(
        root,
        textvariable=self.status_var,
        font=("Arial", 9, "italic"),
        anchor=tk.W,
        padx=15,
        pady=5,
        bg="#e2e8f0",
    )
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)

  def start_search(self):
    username = self.username_entry.get().strip()
    if not username:
      messagebox.showerror("Error", "Please enter a valid username to search.")
      return

    self.search_button.config(state=tk.DISABLED)
    self.output_area.delete(1.0, tk.END)
    self.status_var.set(f"Status: Scanning platforms for '{username}'...")

    threading.Thread(
        target=self.execute_search_thread, args=(username,), daemon=True
    ).start()

  def execute_search_thread(self, username):
    results = []

    for site_name, url_template in TARGET_SITES.items():
      profile_url = url_template.format(username)
      status = "✗ Not Found"

      try:
        if site_name == "TikTok":
          ua = (
              "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X)"
              " AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
          )
        else:
          ua = (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/120.0.0.0 Safari/537.36"
          )

        headers = {
            "User-Agent": ua,
            "Accept-Language": "en-US,en;q=0.9",
        }

        req = urllib.request.Request(profile_url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=6) as response:
          if response.status == 200:
            html_content = (
                response.read().decode("utf-8", errors="ignore").lower()
            )

            if site_name == "GitHub":
              if (
                  "not found" not in html_content
                  and "we couldn't find that page" not in html_content
                  and "contrib" in html_content
              ):
                status = "✔ Found"
            elif site_name == "GitLab":
              if (
                  "page not found" not in html_content
                  and "user not found" not in html_content
              ):
                status = "✔ Found"
            elif site_name == "Instagram":
              if (
                  "sorry, this page isn't available" not in html_content
                  and "page not found" not in html_content
                  and "the link you followed may be broken" not in html_content
              ):
                status = "✔ Found"
            elif site_name == "TikTok":
              if (
                  "couldn't find this account" not in html_content
                  and "user not found" not in html_content
                  and "page not found" not in html_content
                  and "no account found" not in html_content
              ):
                status = "✔ Found"
            elif site_name == "YouTube":
              if (
                  "not found" not in html_content
                  and "this channel does not exist" not in html_content
                  and "channel doesn't exist" not in html_content
              ):
                status = "✔ Found"
            elif site_name == "Steam":
              if (
                  "the specified profile could not be found" not in html_content
                  and "profile not found" not in html_content
              ):
                status = "✔ Found"
            elif site_name == "Chess.com":
              if (
                  "member not found" not in html_content
                  and "page not found" not in html_content
              ):
                status = "✔ Found"
            elif site_name == "Medium":
              if (
                  "looking for something on medium" not in html_content
                  and "out of nothing, something" not in html_content
              ):
                status = "✔ Found"

      except Exception:
        status = "✗ Not Found"

      results.append({
          "Platform": site_name,
          "Status": status,
          "Profile URL": profile_url,
      })

    self.root.after(0, lambda: self.display_results(username, results))

  def display_results(self, username, results):
    found_matches = [r for r in results if "✔" in r["Status"]]

    report_lines = []
    report_lines.append(f"SEARCH RESULTS FOR: {username}")
    report_lines.append("=" * 78)
    report_lines.append(f"{'Platform':<12} | {'Status':<12} | {'Profile URL'}")
    report_lines.append("-" * 78)

    for r in results:
      report_lines.append(
          f"{r['Platform']:<12} | {r['Status']:<12} | {r['Profile URL']}"
      )

    report_lines.append("=" * 78)
    report_lines.append(f"--- Summary ---")
    report_lines.append(f"Total Platforms Checked: {len(results)}")
    report_lines.append(f"Total Matches Found: {len(found_matches)}")
    report_lines.append("=" * 78)

    full_report = "\n".join(report_lines)
    self.output_area.insert(tk.END, full_report)
    self.status_var.set("Status: Search completed accurately.")
    self.search_button.config(state=tk.NORMAL)


if __name__ == "__main__":
  root = tk.Tk()
  app = UserTraceApp(root)
  root.mainloop()