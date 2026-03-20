import json

ts_path = r"c:\Users\PatricioLobos\AppData\Roaming\Code\User\workspaceStorage\f12160a2f4b05640dc88e2a69685ced0\GitHub.copilot-chat\chat-session-resources\b0c31692-ef65-4f5f-a7c5-cfea87f660b4\toolu_vrtx_01WT1q1dstnw3vas8ncp98bX__vscode-1773873273740\content.json"
ps_path = r"c:\Users\PatricioLobos\AppData\Roaming\Code\User\workspaceStorage\f12160a2f4b05640dc88e2a69685ced0\GitHub.copilot-chat\chat-session-resources\b0c31692-ef65-4f5f-a7c5-cfea87f660b4\toolu_vrtx_01KtGoyJQN469x6jmUFRGzF7__vscode-1773873273745\content.json"

print("=" * 70)
print("TIMESTEP SWEEP (N=30)")
print("=" * 70)
with open(ts_path) as f:
    ts = json.load(f)
print(f"Elapsed: {ts['elapsed_ms']} ms, {len(ts['steps'])} steps")
print(f"{'dt_factor':>10} {'integ_const':>12} {'noise_scale':>12} {'dt_value':>10} {'mean_rel_err':>12}")
for s in ts["steps"]:
    print(f"{s['dt_factor']:>10.2f} {s['integ_const']:>12d} {s['noise_scale']:>12d} {s['dt_value']:>10.6f} {s['mean_relative_var_error']:>12.6f}")

print()
print("=" * 70)
print("PRECISION SWEEP (N=30)")
print("=" * 70)
with open(ps_path) as f:
    ps = json.load(f)
print(f"Elapsed: {ps['elapsed_ms']} ms, {len(ps['steps'])} steps")
print(f"{'frac_bits':>10} {'quant_step':>12} {'snr_db':>8} {'mean_rel_err':>12}")
for s in ps["steps"]:
    print(f"{s['fractional_bits']:>10d} {s['quant_step']:>12.10f} {s['snr_db']:>8.1f} {s['mean_relative_var_error']:>12.6f}")
