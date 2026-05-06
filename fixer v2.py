import csv
import os
import traceback
from lxml import etree
from colorama import Fore, Style, init

init(autoreset=True)

csv_file = "dados.csv"
cstats_validos = {"352", "359", "318", "327"}

log_file = "log_execucao.txt"

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def extrair_impostos(xml_str):
    try:
        root = etree.fromstring(xml_str.encode("utf-8"))

        ibs = None
        cbs = None

        for el in root.iter():
            tag = etree.QName(el).localname

            if tag == "vIBS":
                ibs = el.text
            elif tag == "vCBS":
                cbs = el.text

        return ibs, cbs

    except Exception as e:
        return None, None


def aplicar_impostos(xml_path, ibs, cbs, destino):
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()

    alterou = False

    for el in root.iter():
        tag = etree.QName(el).localname

        if tag == "vIBS" and ibs:
            el.text = ibs
            alterou = True

        if tag == "vCBS" and cbs:
            el.text = cbs
            alterou = True

    if alterou:
        tree.write(destino, encoding="utf-8", xml_declaration=True)

    return alterou


try:
    pasta_xmls = input("Pasta dos XMLs originais: ").strip()
    pasta_saida = input("Pasta destino dos XMLs corrigidos: ").strip()

    os.makedirs(pasta_saida, exist_ok=True)

    total = 0
    corrigidos = 0
    ignorados = 0
    erros = 0

    print(Fore.CYAN + "\nIniciando processamento...\n")

    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total += 1

            try:
                cstat = row.get("sefaz_cstat", "").strip()
                id_nf = row.get("id_nfcom_na_mensageria", "").strip()
                xml_corrigido = row.get("XML_CORRIGIDO", "").strip()

                if cstat not in cstats_validos:
                    ignorados += 1
                    continue

                if not id_nf or not xml_corrigido:
                    raise Exception("Dados incompletos")

                ibs, cbs = extrair_impostos(xml_corrigido)

                if not ibs and not cbs:
                    raise Exception("IBS/CBS não encontrados")

                caminho_xml = os.path.join(pasta_xmls, f"{id_nf}.xml")

                if not os.path.exists(caminho_xml):
                    raise Exception("XML não encontrado")

                destino = os.path.join(pasta_saida, f"{id_nf}.xml")

                alterado = aplicar_impostos(caminho_xml, ibs, cbs, destino)

                if alterado:
                    corrigidos += 1
                    print(Fore.GREEN + f"[OK] {id_nf}")
                else:
                    raise Exception("Tag IBS/CBS não encontrada no XML")

            except Exception as e:
                erros += 1
                erro_msg = f"[ERRO] Linha {total} | ID {row.get('id_nfcom_na_mensageria')} | {str(e)}"
                print(Fore.RED + erro_msg)
                log(erro_msg)
                log(traceback.format_exc())

            if total % 50 == 0:
                print(
                    Fore.YELLOW +
                    f"Progresso -> Total: {total} | OK: {corrigidos} | Ignorados: {ignorados} | Erros: {erros}"
                )

    print(Fore.CYAN + "\n===== FINAL =====")
    print(Fore.GREEN + f"Corrigidos: {corrigidos}")
    print(Fore.YELLOW + f"Ignorados: {ignorados}")
    print(Fore.RED + f"Erros: {erros}")
    print(Fore.CYAN + f"Log salvo em: {log_file}")

except Exception as e:
    print(Fore.RED + "\nERRO CRÍTICO:")
    print(str(e))
    log("ERRO CRÍTICO:")
    log(traceback.format_exc())

input(Fore.CYAN + "\nPressiona ENTER pra fechar...")