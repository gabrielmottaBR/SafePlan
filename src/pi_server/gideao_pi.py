# -*- coding: utf-8 -*-
# Biblioteca para facilitar a aquisiçao de dados do PI ou do AF
# Petrobras - RES/EE - Projeto GEMEO - 17/05/2021
# Adaptado para SafePlan - 2026

#%% Importacoes
import sys
import json
import os
import clr
import pandas as pd
import logging

logger = logging.getLogger(__name__)

#%% Configurações e referecias

def load_config():
    """Carrega configuração do gideaoPI"""
    config_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'config',
        'config_gideaopi.json'
    )

    with open(config_path) as f:
        dataConfig = json.load(f)

    return dataConfig

dataConfig = load_config()

sys.path.append(dataConfig['path_pi'])
clr.AddReference(dataConfig['af_sdk'])

from OSIsoft.AF import *
from OSIsoft.AF.PI import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *
from OSIsoft.AF.UnitsOfMeasure import *

attrUM = PICommonPointAttributes.EngineeringUnits
conexoes_pi = []
conexoes_af = []

#%% Métodos

def getServidor(nome, tipo="PI"):
    """
    Definição
    ----------
    Método para obter objeto de conexão com servidor PI ou AF

    Parameters
    ----------
    nome : STRING
            NOME DO SERVIDOR
    tipo : STRING, optional
        TIPO DO SERVIDOR PI IY AF. The default is "PI".

    Returns
    -------
    servidor : OSIsoft.AF.PI.PIServer / OSIsoft.AF.PISystem
        OBJETO SERVIDOR.
    Exemplos
    ----------
    exemplo 1:

        import gideaoPI as gp

        servidorPI = gp.getServidor('SESAUPI01',"PI")

        servidorAF = gp.getServidor('SAURIOPIAF02','AF')
    """
    try:
        global conexoes_pi, conexoes_af
        myPISystem = PISystems()
        if nome:
            if tipo == "PI":
                lista = [a for a in conexoes_pi if a.get_Name().lower() == nome.lower()]
                if lista:
                    servidor = lista[0]
                    logger.info(f'✓ PI Server {nome} já conectado (cache)')
                else:
                    logger.info(f'Conectando ao PI Server {nome}...')
                    servidor = PIServer.FindPIServer(myPISystem.DefaultPISystem, nome)
                    if servidor:
                        conexoes_pi.append(servidor)
                        logger.info(f'✓ Conectado ao PI Server: {nome}')
            elif tipo == "AF":
                lista = [a for a in conexoes_af if a.get_Name().lower() == nome.lower()]
                if lista:
                    servidor = lista[0]
                    logger.info(f'✓ AF Server {nome} já conectado (cache)')
                else:
                    logger.info(f'Conectando ao AF Server {nome}...')
                    servidor = myPISystem[nome]
                    if servidor:
                        conexoes_af.append(servidor)
                        logger.info(f'✓ Conectado ao AF Server: {nome}')
        else:
            servidor = None
    except Exception as e:
        logger.error(f'Erro ao conectar {tipo} Server {nome}: {e}')
        servidor = None
    return servidor

def getAFDataBase(nome, piAFLocal):
    """
    Definição
    ----------
    Método para aquisitar objeto database do AF

    Parameters
    ----------
    nome : STRING
        Nome de um database de um servidor AF.
    piAFLocal : OSIsoft.AF.PISystem
        objeto do servidor AF conectado.

    Returns
    -------
    DB : OSIsoft.AF.AFDatabase
        databse do AF.

    Exemplos
    ----------
    exemplo1:

           import gideaoPI as gp

           meudb = gp.getAFDataBase("DB_BUZIOS_SENSORES", gp.getServidor('SAURIOPIAF02','AF'))

    """
    try:
        DB = piAFLocal.Databases.get_Item(nome)
        logger.info(f'✓ Database {nome} obtido')
        return DB
    except Exception as e:
        logger.error(f'Erro ao obter database {nome}: {e}')
        return None

def identificaTipo(servidor):
    """
    Definição
    ----------
    Método que identificad se o objeto de conexão é um servidor PI ou database AF.

    Parameters
    ----------
    servidor : OSIsoft.AF.PI.PIServer / OSIsoft.AF.AFDatabase
        OBJETO DE CONEXÃO SERVIDOR PI OU DATABASE AF

    Returns
    -------
    tipo : STRING
        'PI' SE OBJETO SERVIDOR PI OU 'AF' DE O SERVIDOR É AF.

    Exemplos
    ----------
    Exemplo 1:

        import gideaoPI as gp

        tipo = gp.idenficaTipo(gp.getServidor('SESAUPI01','PI'))

        tipo = gp.identificaTipo(gp.getAFDataBase('DB_BUZIOS_SENSORES',gp.getServidor('SAURIOPIAF02',tipo='AF')))
    """
    tipo=None
    if servidor.__class__.__name__ == 'PIServer':
        tipo = 'PI'
    elif servidor.__class__.__name__ == 'AFDatabase':
        tipo = 'AF'
    return tipo

def converteNumero(texto, flag=False):
    """
    Definição
    ----------
    Método que converte saídas binárias de modo texto em saídas '0' ou '1'.

    Parameters
    ----------
    texto : STRING
        SAÍDA STRING DO PI OU AF.
    flag : BOOLEANO, optional
        DEFINE SE IRÁ CONVERTER OU NÃO. The default is False (não converte).

    Returns
    -------
    saida : STRING (a partir de float)
        '0.0' OU '1.0'.

    """
    try:
        if flag:
            if str(texto) in ['1','On','ON','on','Aberto','ABERTO','Ligado','LIGADO']:
                saida = 1.00
            elif str(texto) in ['0','Off','OFF','off','Fechado','FECHADO','Desligado','DESLIGADO','Normal']:
                saida = 0.00
            else:
                saida = float(texto)
        else:
            saida = texto

    except:
        saida = texto
    return saida

def pathToAtributoAF(DB, caminho_piAF):
    """Converte path AF para atributo"""
    caminho_piAF = caminho_piAF.replace("\\\\",'')
    caminho_piAF = caminho_piAF.replace("\\",'\\\\')
    lista=caminho_piAF.split('|')
    lista_elementos = lista[0].split('\\\\')
    if len(lista[1].split('\\\\'))>1:
        elemento_final = lista[1].split('\\\\')[0]
        atributo = lista[1].split('\\\\')[1]
    else:
        atributo = lista[1]
        elemento_final = lista_elementos[-1]
        lista_elementos = lista_elementos[:-1]
    element = DB.Elements.get_Item(lista_elementos[2])
    for el in lista_elementos[3:]:
        element = element.Elements.get_Item(el)
    element = element.Elements.get_Item(elemento_final)
    attribute = element.Attributes.get_Item(atributo)
    return attribute

def getValorCorrentePI(servidor_pi, tag, isNumeric):
    """Obtém valor corrente de um tag PI"""
    valor = None
    try:
        pt = PIPoint.FindPIPoint(servidor_pi, tag)
        current_value = pt.CurrentValue()
        valor = current_value.Value
        valor = converteNumero(valor, isNumeric)
    except Exception as e:
        logger.error(f'Erro ao obter valor de {tag}: {e}')
        valor = None
    return str(valor)

def getAFAttributeValue(DB, caminho_piAF, isNumeric):
    """Obtém valor de um atributo AF"""
    try:
        attribute = pathToAtributoAF(DB, caminho_piAF)
        valor=str(attribute.GetValue())
        valor = converteNumero(valor, isNumeric)
    except Exception as e:
        logger.error(f'Erro ao obter valor AF: {e}')
        valor =  None
    return valor

def getValorCorrente(servidorOUdb, tagOUAttr, isNumeric=False):
    r"""
    Definição
    ----------
    Aquisita o valor atual de uma tag PI ou atributo AF.

    Parameters
    ----------
    servidorOUdb : OSIsoft.AF.PI.PIServer / OSIsoft.AF.AFDatabase
        DESCRIPTION objeto de conexão com um servidor PI ou database AF.
    tagOUAttr : TYPE String
        DESCRIPTION Tag PI de um sensor ou atributo AF.
    isNumeric : TYPE Boolean
        DESCRIPTION Indica se vai querer converter potencial saída binária de forma texto para '0.0' ou '1.0'.

    Returns
    -------
    TYPE String
        DESCRIPTION Valor snapshot do PI.
    """
    try:
        if servidorOUdb:
            tipo = identificaTipo(servidorOUdb)
            if tipo == 'PI':
                valor = getValorCorrentePI(servidorOUdb, tagOUAttr, isNumeric)
            elif tipo == 'AF':
                valor = getAFAttributeValue(servidorOUdb, tagOUAttr, isNumeric)
            else:
                logger.error('tipo nao identificado')
                valor = None
        else:
            valor = None
    except Exception as e:
        logger.error(f'Erro em getValorCorrente: {e}')
        valor = None
    return valor

def getRecordedPI(servidor_pi, tag, inicio, fim, isNumeric):
    """Obtém valores armazenados do PI"""
    timerange = AFTimeRange(inicio, fim)
    try:
        pt = PIPoint.FindPIPoint(servidor_pi, tag)
        recorded = pt.RecordedValues(timerange, AFBoundaryType.Inside, "", False)
        data = list(map(lambda x: (x.Timestamp.LocalTime.ToString(),converteNumero(str(x.Value),isNumeric)), recorded))
        dfValor = pd.DataFrame(data, columns=['timestamp','valor'])
    except Exception as e:
        logger.error(f'Erro em getRecordedPI: {e}')
        dfValor = None
    return dfValor

def getRecordedAF(DB, caminho_piAF, inicio, fim, isNumeric):
    """Obtém valores armazenados do AF"""
    tr = AFTimeRange()
    tr.StartTime = AFTime(inicio)
    tr.EndTime = AFTime(fim)
    try:
        attribute = pathToAtributoAF(DB, caminho_piAF)
        recorded =attribute.Data.RecordedValues(tr, AFBoundaryType.Inside, None,'', False,0)
        data = list(map(lambda x: (x.Timestamp.LocalTime.ToString(),converteNumero(str(x.Value),isNumeric)), recorded))
        dfValor = pd.DataFrame(data, columns=['timestamp','valor'])
    except Exception as e:
        logger.error(f'Erro em getRecordedAF: {e}')
        dfValor=None
    return dfValor

def getValoresArmazenados(servidorOUdb, tagOUAttr, inicio, fim, isNumeric=False):
    r"""
    Definição
    ----------
    Aquisita valores aramezenados de uma tag PI ou atributo AF num intervalo entre uma data de inicio e fim.

    Parameters
    ----------
    servidorOUdb : OSIsoft.AF.PI.PIServer / OSIsoft.AF.AFDatabase
        DESCRIPTION objeto de conexão com um servidor PI ou database AF.
    tagOUAttr : TYPE String
        DESCRIPTION Tag PI de um sensor ou atributo AF.
    inicio : TYPE String
        DESCRIPTION string com  o datetime do inicio do periodo, pode-se usar  sintaxe de tempo do PI.
    fim : TYPE String
        DESCRIPTION string com  o datetime do fim do periodo, pode-se usar  sintaxe de tempo do PI.
    isNumeric : TYPE Boolean
        DESCRIPTION Indica se vai querer converter potencial saída binária de forma texto para '0.0' ou '1.0'.

    Returns
    -------
    TYPE pandas dataframe
        DESCRIPTION dataframe dom o timestamp e valores aquisitados.
    """
    valor=None
    try:
        tipo = identificaTipo(servidorOUdb)
        if tipo == 'PI':
            logger.debug('tipo PI identificado')
            valor = getRecordedPI(servidorOUdb, tagOUAttr, inicio, fim, isNumeric)
        elif tipo == 'AF':
            valor = getRecordedAF(servidorOUdb, tagOUAttr, inicio, fim, isNumeric)
        else:
            logger.error('tipo nao identificado')
    except Exception as e:
        logger.error(f'Erro em getValoresArmazenados: {e}')
    return valor

def getInterpolatedPI(servidor_pi, tag, inicio, fim, intervalo, isNumeric):
    """Obtém valores interpolados do PI"""
    timerange = AFTimeRange(inicio, fim)
    span = AFTimeSpan.Parse(intervalo)
    try:
        pt = PIPoint.FindPIPoint(servidor_pi, tag)
        interpolated = pt.InterpolatedValues(timerange, span, "", False)
        data = list(map(lambda x: (x.Timestamp.LocalTime.ToString(),converteNumero(str(x.Value),isNumeric)), interpolated))
        dfValor = pd.DataFrame(data, columns=['timestamp','valor'])
    except Exception as e:
        logger.error(f'Erro em getInterpolatedPI: {e}')
        dfValor = None
    return dfValor

def getInterpolatedAF(DB, caminho_piAF, inicio, fim, intervalo, isNumeric):
    """Obtém valores interpolados do AF"""
    tr = AFTimeRange()
    tr.StartTime = AFTime(inicio)
    tr.EndTime = AFTime(fim)
    span = AFTimeSpan.Parse(intervalo)
    try:
        attribute = pathToAtributoAF(DB, caminho_piAF)
        recorded = attribute.Data.InterpolatedValues(tr, span, None,'', False)
        data = list(map(lambda x: (x.Timestamp.LocalTime.ToString(),converteNumero(str(x.Value),isNumeric)), recorded))
        dfValor = pd.DataFrame(data, columns=['timestamp','valor'])
    except Exception as e:
        logger.error(f'Erro em getInterpolatedAF: {e}')
        dfValor=None
    return dfValor

def getValoresInterpolados(servidorOUdb, tagOUAttr, inicio, fim, intervalo, isNumeric=False):
    r"""
    Definição
    ----------
    Aquisita valores interpolados de uma tag PI ou atributo AF num intervalo entre uma data de inicio e fim e em um intervalo determinado.

    Parameters
    ----------
    servidorOUdb : OSIsoft.AF.PI.PIServer / OSIsoft.AF.AFDatabase
        DESCRIPTION objeto de conexão com um servidor PI ou database AF.
    tagOUAttr : TYPE String
        DESCRIPTION Tag PI de um sensor ou atributo AF.
    inicio : TYPE String
        DESCRIPTION string com  o datetime do inicio do periodo, pode-se usar  sintaxe de tempo do PI.
    fim : TYPE String
        DESCRIPTION string com  o datetime do fim do periodo, pode-se usar  sintaxe de tempo do PI.
    intervalo : TYPE String
        DESCRIPTION string com o intervalo para aquisição dos dados iterpolados ('1m','1h','2s', ...).
    isNumeric : TYPE Boolean
        DESCRIPTION Indica se vai querer converter potencial saída binária de forma texto para '0.0' ou '1.0'.

    Returns
    -------
    TYPE Pandas dataframe
        DESCRIPTION dataframe com o timestamp e valores aquisitados.
    """
    valor=None
    try:
        tipo = identificaTipo(servidorOUdb)
        if tipo == 'PI':
            valor = getInterpolatedPI(servidorOUdb, tagOUAttr, inicio, fim, intervalo, isNumeric)
        elif tipo == 'AF':
            valor = getInterpolatedAF(servidorOUdb, tagOUAttr, inicio, fim, intervalo, isNumeric)
        else:
            logger.error('tipo nao identificado')
    except Exception as e:
        logger.error(f'Erro em getValoresInterpolados: {e}')
    return valor

def getUMPI(servidor_pi, tag):
    """Obtém unidade de medida do PI"""
    valor= ''
    try:
        pt = PIPoint.FindPIPoint(servidor_pi, tag)
        pt.LoadAttributes(None)
        um = pt.GetAttribute(attrUM)
        valor = um
    except Exception as e:
        logger.error(f'Erro em getUMPI: {e}')
        valor = ''
    return valor

def getUMAF(DB, caminho_piAF):
    """Obtém unidade de medida do AF"""
    valor = ''
    try:
        attribute = pathToAtributoAF(DB, caminho_piAF)
        valor = attribute.DefaultUOM.ToString()
    except Exception as e:
        logger.error(f'Erro em getUMAF: {e}')
        valor=None
    return valor

def getUM(servidorOUdb, tagOUAttr):
    r"""
    Definição
    ----------
    Retorna  a unidade de medida de engenharia de uma tag PI ou atributo AF.

    Parameters
    ----------
    servidorOUdb : OSIsoft.AF.PI.PIServer / OSIsoft.AF.AFDatabase
        DESCRIPTION objeto de conexão com um servidor PI ou database AF.
    tagOUAttr : TYPE String
        DESCRIPTION Tag PI de um sensor ou atributo AF.

    Returns
    -------
    valor : TYPE String
        DESCRIPTION Unidade de engenharia do PI ou AF.
    """
    try:
        if servidorOUdb:
            tipo = identificaTipo(servidorOUdb)
            if tipo == 'PI':
                valor = getUMPI(servidorOUdb, tagOUAttr)
            elif tipo == 'AF':
                valor = getUMAF(servidorOUdb, tagOUAttr)
            else:
                logger.error('tipo nao identificado')
                valor = ''
        else:
            valor = ''
            logger.error('Falha na conexão com o servidor especificado.')
    except Exception as e:
        logger.error(f'Erro em getUM: {e}')
        valor = ''
    return valor
