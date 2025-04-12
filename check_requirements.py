import pkg_resources
import subprocess

def install_missing_packages(requirements_file='requirements.txt'):
    try:
        with open(requirements_file, 'r') as f:
            packages = f.read().splitlines()

        for package in packages:
            try:
                pkg_resources.require(package)
                print(f"{package} zaten yüklü.")
            except pkg_resources.DistributionNotFound:
                print(f"{package} eksik, yükleniyor...")
                subprocess.check_call(["pip", "install", package])
            except pkg_resources.VersionConflict as e:
                print(f"{package} için versiyon uyuşmazlığı: {e}. Güncelleniyor...")
                subprocess.check_call(["pip", "install", "--upgrade", package])
    except FileNotFoundError:
        print(f"'{requirements_file}' dosyası bulunamadı.")

if __name__ == "__main__":
    install_missing_packages()
