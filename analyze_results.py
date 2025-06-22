import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import os
import datetime




class ExperimentAnalyzer:
    def __init__(self, results_dir, population_size=50, success_threshold=10):
        self.results_dir = Path(results_dir)
        self.population_size = population_size
        self.success_threshold = success_threshold
        self.results = self._load_results()

    def _load_results(self):
        algorithms = [d.name for d in self.results_dir.iterdir() if d.is_dir()]
        data = []

        for algo in algorithms:
            for trial_file in (self.results_dir / algo).glob("trial_*.json"):
                with open(trial_file) as f:
                    trial_data = json.load(f)

                    df_iter = pd.DataFrame(trial_data.get("iteration_log", []))
                    total_iterations = 0
                    if not df_iter.empty:
                        grouped = df_iter.groupby(['week', 'module_id'])['iteration'].max()
                        total_iterations = (grouped + 1).sum()  # +1 karena 0-indexed

                    data.append({
                        "algorithm": algo,
                        "trial": int(trial_file.stem.split("_")[1]),
                        "final_fitness": trial_data.get("final_fitness", None),
                        "computation_time": trial_data.get("computation_time", None),
                        "total_iterations": total_iterations,
                        "success": trial_data.get("final_fitness", float('inf')) < self.success_threshold
                    })

        return pd.DataFrame(data)

    def calculate_metrics(self):
        metrics = []
        for algo in self.results["algorithm"].unique():
            algo_data = self.results[self.results["algorithm"] == algo]
            successful = algo_data[algo_data["success"]]
            if not successful.empty:
                aes = (successful["total_iterations"] * self.population_size).mean()
            else:
                aes = np.nan

            metrics.append({
                "algorithm": algo,
                "MBF": algo_data["final_fitness"].mean(),
                "MBF_std": algo_data["final_fitness"].std(),
                "AES": aes,
                "SR": algo_data["success"].mean() * 100,
                "avg_time": algo_data["computation_time"].mean(),
                "time_std": algo_data["computation_time"].std()
            })

        return pd.DataFrame(metrics)

    def analyze_per_algorithm(self):
        per_algo_stats = {}
        output_dir = self.results_dir / "per_algorithm"
        output_dir.mkdir(exist_ok=True)

        for algo in self.results["algorithm"].unique():
            algo_data = self.results[self.results["algorithm"] == algo]
            stats = {
                "fitness": algo_data["final_fitness"].describe().to_dict(),
                "computation_time": algo_data["computation_time"].describe().to_dict(),
                "iterations": algo_data["total_iterations"].describe().to_dict(),
                "success_rate": algo_data["success"].mean() * 100
            }

            per_algo_stats[algo] = stats

            # Save JSON
            with open(output_dir / f"{algo}_stats.json", "w") as f:
                json.dump(stats, f, indent=2)

            # Save CSV
            algo_data.to_csv(output_dir / f"{algo}_trials.csv", index=False)

        return per_algo_stats

    def _reconstruct_global_convergence(self, iteration_log):
        df = pd.DataFrame(iteration_log)
        if df.empty:
            return []

        df_sorted = df.sort_values(['week', 'module_id', 'iteration'])
        global_best = float('inf')
        fitness_history = []

        for _, row in df_sorted.iterrows():
            if row["best_fitness"] < global_best:
                global_best = row["best_fitness"]
            fitness_history.append(global_best)

        return fitness_history

    def generate_plots(self):
        plt.figure(figsize=(12, 7))
        for algo in self.results["algorithm"].unique():
            histories = []

            for trial_file in (self.results_dir / algo).glob("trial_*.json"):
                with open(trial_file) as f:
                    data = json.load(f)
                    history = self._reconstruct_global_convergence(data.get("iteration_log", []))
                    if history:
                        histories.append(history)

            if histories:
                max_len = max(len(h) for h in histories)
                padded = [h + [h[-1]] * (max_len - len(h)) for h in histories]
                avg_history = np.mean(padded, axis=0)
                plt.plot(avg_history, label=algo)

        plt.title("Convergence (Average Global Best Fitness)")
        plt.xlabel("Global Iteration Step")
        plt.ylabel("Best Fitness")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(self.results_dir / "convergence_comparison.png")
        plt.close()

        # Boxplots
        for column, title, ylabel, filename in [
            ("final_fitness", "Final Fitness Comparison", "Fitness", "fitness_comparison.png"),
            ("computation_time", "Computation Time Comparison", "Time (s)", "time_comparison.png")
        ]:
            plt.figure(figsize=(10, 6))
            self.results.boxplot(column=column, by="algorithm")
            plt.title(title)
            plt.suptitle("")
            plt.ylabel(ylabel)
            plt.tight_layout()
            plt.savefig(self.results_dir / filename)
            plt.close()
            
    def generate_algorithm_plots(self):
        output_dir = self.results_dir / "per_algorithm"
        output_dir.mkdir(exist_ok=True)

        for algo in self.results["algorithm"].unique():
            histories = []

            for trial_file in (self.results_dir / algo).glob("trial_*.json"):
                with open(trial_file) as f:
                    data = json.load(f)
                    history = self._reconstruct_global_convergence(data.get("iteration_log", []))
                    if history:
                        histories.append(history)

            if not histories:
                continue

            # Padding histories to same length
            max_len = max(len(h) for h in histories)
            padded = [h + [h[-1]] * (max_len - len(h)) for h in histories]
            avg_history = np.mean(padded, axis=0)

            # Save individual plot
            plt.figure(figsize=(10, 6))
            for h in padded:
                plt.plot(h, alpha=0.2, color="gray", linewidth=1)
            plt.plot(avg_history, label=f"Average ({algo})", color="blue", linewidth=2)
            plt.title(f"Fitness Convergence – {algo}")
            plt.xlabel("Global Iteration Step")
            plt.ylabel("Best Fitness")
            plt.legend()
            plt.grid()
            plt.tight_layout()

            plot_path = output_dir / f"{algo}_convergence.png"
            plt.savefig(plot_path)
            plt.close()
            
    def generate_radar_chart(self):
        metrics_df = self.calculate_metrics()
        if metrics_df.empty:
            print("No metrics to plot.")
            return

        # Ekstrak metrik
        algorithms = metrics_df["algorithm"].tolist()
        mbf = metrics_df["MBF"].tolist()
        aes = metrics_df["AES"].tolist()
        sr = metrics_df["SR"].tolist()
        time = metrics_df["avg_time"].tolist()

        # Normalisasi data (semua dibalik agar makin besar makin bagus)
        max_mbf = max(mbf)
        max_aes = max(aes)
        max_time = max(time)

        mbf_norm = [1 - (x / max_mbf) if not np.isnan(x) else 0 for x in mbf]
        aes_norm = [1 - (x / max_aes) if not np.isnan(x) else 0 for x in aes]
        sr_norm = [x / 100 if not np.isnan(x) else 0 for x in sr]
        time_norm = [1 - (x / max_time) if not np.isnan(x) else 0 for x in time]

        # Radar chart data
        labels = ['Fitness\n(MBF)', 'Evaluasi\n(AES)', 'Tingkat\nKeberhasilan', 'Waktu\nEksekusi']
        data = np.array([mbf_norm, aes_norm, sr_norm, time_norm])
        data = np.transpose(data)

        # Radar chart settings
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        data = np.concatenate((data, data[:, [0]]), axis=1)  # Repeat first column
        angles += angles[:1]

        # Plotting
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        for i in range(len(algorithms)):
            ax.plot(angles, data[i], label=algorithms[i], linewidth=2)
            ax.fill(angles, data[i], alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_yticklabels([])
        ax.set_title('Perbandingan Kinerja Algoritma Hybrid dan GA', fontsize=14)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))

        plt.tight_layout()
        output_path = self.results_dir / "radar_comparison.png"
        plt.savefig(output_path)
        plt.close()
        print(f"📈 Radar chart saved to: {output_path}")


    def export_algorithm_html_reports(self):
        output_dir = self.results_dir / "per_algorithm"
        for algo in self.results["algorithm"].unique():
            algo_data = self.results[self.results["algorithm"] == algo]

            if algo_data.empty:
                continue

            stats = algo_data.describe().to_html(classes="stats", border=0)

            html = f"""
            <html>
            <head>
                <title>Report - {algo}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        line-height: 1.6;
                    }}
                    h1 {{
                        color: #2c3e50;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin-top: 20px;
                        margin-bottom: 30px;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #3498db;
                        color: white;
                    }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        margin-top: 20px;
                    }}
                    .note {{
                        font-size: 0.9em;
                        color: gray;
                    }}
                </style>
            </head>
            <body>
                <h1>Algorithm Report: {algo}</h1>
                <p><strong>Total Trials:</strong> {len(algo_data)}</p>
                <p><strong>Success Rate:</strong> {algo_data['success'].mean() * 100:.2f}%</p>
                <h2>Summary Statistics</h2>
                {stats}
                <h2>Fitness Convergence</h2>
                <img src="{algo}_convergence.png" alt="Convergence Graph">
                <p class="note">Lines in gray = individual trials, blue = average.</p>
            </body>
            </html>
            """

            html_path = output_dir / f"{algo}_report.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"📊 HTML report generated for {algo}: {html_path}")


    def export_html_report(self, output_file="report.html"):
        metrics_df = self.calculate_metrics()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
        <html>
        <head>
            <title>Hybrid Scheduling Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}
                h1, h2 {{
                    color: #2c3e50;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 30px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                img {{
                    max-width: 100%;
                    height: auto;
                    margin-bottom: 30px;
                }}
            </style>
        </head>
        <body>
            <h1>Hybrid Metaheuristic Scheduling Report</h1>
            <p><strong>Generated:</strong> {now}</p>

            <h2>1. Summary Metrics</h2>
            {metrics_df.to_html(index=False)}

            <h2>2. Convergence Plot</h2>
            <img src="convergence_comparison.png" alt="Convergence Comparison">

            <h2>3. Final Fitness Boxplot</h2>
            <img src="fitness_comparison.png" alt="Fitness Comparison">

            <h2>4. Computation Time Boxplot</h2>
            <img src="time_comparison.png" alt="Time Comparison">
            
            <h2>5. Radar Chart</h2>
            <img src="radar_comparison.png" alt="Radar Comparison">
            <p class="note">Note: All metrics are averaged across trials.</p>
            
            <h2>6. Detailed Statistics</h2>
            <h3>Fitness Statistics</h3>
            <pre>{json.dumps(self.results.groupby("algorithm")["final_fitness"].describe().to_dict(), indent=2)}</pre>
            <h3>Time Statistics</h3>
            <pre>{json.dumps(self.results.groupby("algorithm")["computation_time"].describe().to_dict(), indent=2)}</pre>
            <h3>Iterations Statistics</h3>
            <pre>{json.dumps(self.results.groupby("algorithm")["total_iterations"].describe().to_dict(), indent=2)}</pre>
            <p class="note">Note: All statistics are calculated per algorithm.</p>
            
            
            
        </body>
        </html>
        """

        html_path = self.results_dir / output_file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"📄 HTML report saved to: {html_path}")

    def save_report(self):
        metrics_df = self.calculate_metrics()
        self.generate_plots()
        per_algorithm_stats = self.analyze_per_algorithm()

        report = {
            "summary_metrics": metrics_df.to_dict(orient="records"),
            "per_algorithm": per_algorithm_stats,
            "detailed_stats": {
                "fitness": self.results.groupby("algorithm")["final_fitness"].describe().to_dict(),
                "time": self.results.groupby("algorithm")["computation_time"].describe().to_dict(),
                "iterations": self.results.groupby("algorithm")["total_iterations"].describe().to_dict()
            },
            "plots": [
                "convergence_comparison.png",
                "fitness_comparison.png",
                "time_comparison.png"
            ]
        }

        with open(self.results_dir / "analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)

        metrics_df.to_csv(self.results_dir / "metrics_summary.csv", index=False)

        print(f"✔️ Report saved to: {self.results_dir}/analysis_report.json")


if __name__ == "__main__":
    analyzer = ExperimentAnalyzer("experiment_results/latest_run")
    analyzer.save_report()
    analyzer.export_html_report("report.html")
    analyzer.generate_algorithm_plots()
    analyzer.export_algorithm_html_reports()
    analyzer.generate_radar_chart()

