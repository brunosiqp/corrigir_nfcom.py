import os
import xml.etree.ElementTree as ET
import traceback

TXT_DIR = r"C:\Users\bruno.siqueira\Desktop\QG's\Cstat 318 XML Fixer\txts"
OUT_DIR = r"C:\Users\bruno.siqueira\Desktop\QG's\Cstat 318 XML Fixer\fixed"


def corrigir_ibsu(xml_path, output_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    ns = {'nfe': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

    for det in root.findall('.//nfe:det' if ns else './/det', ns):

        gIBSUF = det.find('.//nfe:gIBSUF' if ns else './/gIBSUF', ns)
        vBC = det.find('.//nfe:gIBSCBS/nfe:vBC' if ns else './/gIBSCBS/vBC', ns)

        if gIBSUF is None or vBC is None:
            continue

        p = gIBSUF.find('nfe:pIBSUF' if ns else 'pIBSUF', ns)
        v = gIBSUF.find('nfe:vIBSUF' if ns else 'vIBSUF', ns)

        if p is None or v is None:
            continue

        try:
            base = float(vBC.text)
            aliq = float(p.text)

            calculado = round(base * (aliq / 100), 2)

            print(f"Item {det.get('nItem')} -> {v.text} => {calculado:.2f}")

            v.text = f"{calculado:.2f}"

        except Exception as e:
            print(f"Erro no item {det.get('nItem')}: {e}")

    tree.write(output_path, encoding='utf-8', xml_declaration=True)


def processar():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    arquivos = [f for f in os.listdir(TXT_DIR) if f.endswith('.txt')]

    if not arquivos:
        print("Nenhum TXT encontrado")
        return

    for file in arquivos:
        try:
            print(f"\nProcessando: {file}")

            path = os.path.join(TXT_DIR, file)
            out = os.path.join(OUT_DIR, file.replace('.txt', '.xml'))

            corrigir_ibsu(path, out)

            print(f"✔ Corrigido: {out}")

        except Exception:
            print(f"\n💥 ERRO no arquivo {file}")
            traceback.print_exc()

    input("\nENTER pra fechar...")


if __name__ == "__main__":
    processar()