import os
import xml.etree.ElementTree as ET

# ordem correta segundo MOC NFCom
ordem_ide = [
    cUF, cNF, cDV, mod, serie, nNF, dhEmi,
    tpAmb, tpEmis, cMunFG, finNFCom, tpFat,
    verProc, nSiteAutoriz, dhCont, xJust
]

def corrigir_xml(entrada, saida)
    os.makedirs(saida, exist_ok=True)

    for arquivo in os.listdir(entrada)
        if not arquivo.lower().endswith(.xml)
            continue

        caminho = os.path.join(entrada, arquivo)
        try
            tree = ET.parse(caminho)
            root = tree.getroot()

            ide = root.find(.ide)
            if ide is not None
                # pegar tags já existentes (mantendo o último valor, sem duplicatas)
                elementos = {}
                for child in ide
                    elementos[child.tag] = child

                # limpar bloco ide
                for child in list(ide)
