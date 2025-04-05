import streamlit as st
import requests
import json
import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

link = os.getenv("FIREBASE_URL")  # Acessa a variável de ambiente

lista_de_tecnicos = ["Carlos Alberto de Pascoli Filho", "Carlos Alberto de Pascoli", "Gabriela Pereira Evangelista"]

def criar_ordem_servico(local, descricao, solicitante):
    now = datetime.datetime.now()
    dataAtual = now.strftime("%d-%m-%Y")
    horaAtual = now.strftime("%H:%M")
    dados = {
        'local': local,
        'descricao': descricao,
        'status': 'aberta',
        'data': dataAtual,
        'hora': horaAtual,
        'solicitante': solicitante,
        'tecnico': None,
        'horas_conclusao': None
    }
    requisicao = requests.post(f'{link}/ordemServico/.json', data=json.dumps(dados))
    return requisicao

def ler_ordens_servico():
    ordens = requests.get(f'{link}/ordemServico/.json')
    return ordens.json()

def atualizar_status_ordem_servico(id_ordem, novo_status, tecnico=None, horas_conclusao=None):
    dados = {'status': novo_status}
    if tecnico:
        dados['tecnico'] = tecnico
    if horas_conclusao is not None:
        dados['horas_conclusao'] = horas_conclusao
    requisicao = requests.patch(f'{link}/ordemServico/{id_ordem}.json', data=json.dumps(dados))
    return requisicao

def exibir_ordens(ordens_dict, status_filtro=None):
    if ordens_dict:
        for id_ordem, detalhes in ordens_dict.items():
            if status_filtro is None or detalhes['status'] == status_filtro:
                st.subheader(f"Local / Descrição: {detalhes.get('local', 'Não informado')} - {detalhes.get('descricao', 'Não informada')}")
                st.write(f"**Local:** {detalhes.get('local', 'Não informado')}")
                st.write(f"**Descrição:** {detalhes.get('descricao', 'Não informada')}")
                st.write(f"**Solicitante:** {detalhes.get('solicitante', 'Não informado')}")
                st.write(f"**Técnico:** {detalhes.get('tecnico', 'Não informado')}")
                st.write(f"**Data:** {detalhes.get('data', 'Não informada')} - **Hora:** {detalhes.get('hora', 'Não informada')}")
                st.write(f"**Status:** {detalhes.get('status', 'Não informado')}")
                if detalhes['status'] == 'aberta':
                    with st.expander(f"Ações - OS {id_ordem}"):
                        tecnico_conclusao = st.selectbox("Técnico Responsável pela Conclusão", [""] + lista_de_tecnicos, key=f"tecnico_conclusao_{id_ordem}")
                        horas_conclusao = st.number_input("Horas para Conclusão", min_value=0.0, step=0.5, format="%.1f", key=f"horas_{id_ordem}")
                        if st.button("Marcar como Concluída", key=f"concluir_{id_ordem}"):
                            if tecnico_conclusao:
                                atualizar_status_ordem_servico(id_ordem, 'concluida', tecnico=tecnico_conclusao, horas_conclusao=horas_conclusao)
                                st.success(f"OS {id_ordem} marcada como concluída!")
                                st.rerun()  # Recarrega o app para atualizar a lista
                            else:
                                st.warning("Por favor, selecione o técnico responsável pela conclusão.")
                elif detalhes['status'] == 'concluida':
                    st.write(f"**Horas para Conclusão:** {detalhes.get('horas_conclusao', 'Não informado')}")
                st.divider()
    else:
        st.info("Nenhuma ordem de serviço encontrada.")

st.title("Sistema de Atendimento de Ordem de Serviço")

st.sidebar.header("Nova Ordem de Serviço")
with st.sidebar:
    local = st.text_input("Local")
    descricao = st.text_area("Descrição do Problema")
    solicitante = st.text_input("Solicitante")
    if st.button("Criar Ordem de Serviço"):
        if local and descricao and solicitante:
            requisicao = criar_ordem_servico(local, descricao, solicitante)
            if requisicao.status_code == 200:
                st.success("Ordem de serviço criada com sucesso!")
            else:
                st.error(f"Erro ao criar ordem de serviço: {requisicao.text}")
        else:
            st.warning("Por favor, preencha todos os campos.")

st.header("Ordens de Serviço")

# Filtro de status
status_filtro = st.radio("Filtrar por Status:", ["Todas", "Abertas", "Concluídas"], horizontal=True)
filtro = None
if status_filtro == "Abertas":
    filtro = "aberta"
elif status_filtro == "Concluídas":
    filtro = "concluida"

ordens = ler_ordens_servico()
exibir_ordens(ordens, filtro)