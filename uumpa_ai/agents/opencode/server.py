import subprocess


def start():
    p = subprocess.Popen(
        ['opencode', 'serve', '--hostname', '0.0.0.0', '--port', '4096']
    )
    p.wait()
