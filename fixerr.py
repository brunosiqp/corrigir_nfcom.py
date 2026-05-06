import xml.etree.ElementTree as ET
import re
from datetime import datetime

# =========================
# LOG COLORIDO
# =========================
class Cor:
    VERDE = '\033[92m'
    VERMELHO = '\033[91m'
    AMARELO = '\033[93m'
    RESET = '\033[0m'

def log(msg, tipo="INFO"):
    agora = datetime.now().strftime("%H:%M:%S")

    if tipo == "OK":
        print(f"{Cor.VERDE}[{agora}] {msg}{Cor.RESET}")
    elif tipo == "ERRO":
        print(f"{Cor.VERMELHO}[{agora}] {msg}{Cor.RESET}")
    else:
        print(f"{Cor.AMARELO}[{agora}] {msg}{Cor.RESET}")

# =========================
# PARSE TXT
# =========================
def parse_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pairs = re.findall(r'<(\w+)>(.*?)</\1>', content)
    return {tag: val for tag, val in pairs}

# =========================
# FUNÇÕES AUXILIARES
# =========================
def to_float(v):
    try:
        return float(v)
    except:
        return 0.0

def set_if_exists(parent, tag, value):
    el = parent.find(f".//{tag}")
    if el is not None:
        el.text = f"{value:.2f}"

# =========================
# PROCESSAMENTO PRINCIPAL
# =========================
def processar(xml_path, txt_path, output_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        txt_data = parse_txt(txt_path)

        total_base = 0.0
        total_ibs = 0.0
        total_cbs = 0.0

        # =========================
        # LOOP NOS ITENS
        # =========================
        for det in root.findall(".//det"):
            imposto = det.find(".//IBSCBS")
            if imposto is None:
                continue

            g = imposto.find(".//gIBSCBS")
            if g is None:
                continue

            vBC = to_float(g.findtext("vBC"))
            vIBS = to_float(g.findtext("vIBS"))
            vCBS = to_float(g.findtext(".//vCBS"))

            # 🔧 REGRA 1: se base = 0 → zera tudo
            if vBC == 0:
                log("Item com base 0 → zerando impostos")
                set_if_exists(g, "vIBS", 0)
                set_if_exists(g, "vCBS", 0)
                set_if_exists(g, "vIBSUF", 0)
                set_if_exists(g, "pIBSUF", 0)
                vIBS = 0
                vCBS = 0

            # 🔧 REGRA 2: se valor = 0 → zera aliquota
            if vIBS == 0:
                set_if_exists(g, "pIBSUF", 0)

            if vCBS == 0:
                set_if_exists(g, "pCBS", 0)

            total_base += vBC
            total_ibs += vIBS
            total_cbs += vCBS

        log(f"Base total recalculada: {total_base}", "OK")
        log(f"IBS total recalculado: {total_ibs}", "OK")
        log(f"CBS total recalculado: {total_cbs}", "OK")

        # =========================
        # ATUALIZA TOTAL
        # =========================
        total = root.find(".//IBSCBSTot")
        if total is not None:

            set_if_exists(total, "vBCIBSCBS", total_base)
            set_if_exists(total, "vIBS", total_ibs)
            set_if_exists(total, "vCBS", total_cbs)

            # IBS UF total
            set_if_exists(total, "vIBSUF", total_ibs)

        # =========================
        # SALVA
        # =========================
        tree.write(output_path, encoding='utf-8', xml_declaration=True)

        log("XML corrigido e salvo com sucesso", "OK")

    except Exception as e:
        log(f"Erro: {e}", "ERRO")


# =========================
# MAIN LOOP
# =========================
def main():
    while True:
        try:
            xml_path = input("XML original: ").strip()
            txt_path = input("TXT corrigido: ").strip()
            output_path = input("Saída XML: ").strip()

            processar(xml_path, txt_path, output_path)

        except KeyboardInterrupt:
            print("\nSaindo...")
            break


if __name__ == "__main__":
    main()