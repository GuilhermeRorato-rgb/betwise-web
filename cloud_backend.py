"""Busca vetorial portátil e limites para a demonstração pública."""
from contextlib import closing
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path

import numpy as np
import streamlit as st
from google import genai
from google.genai import types


def setting(name, default):
    value = os.environ.get(name)
    if value is not None:
        return value
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


class CloudCollection:
    def __init__(self, directory):
        directory = Path(directory)
        self.documents = json.loads((directory / 'corpus.json').read_text(encoding='utf-8'))
        self.meta = json.loads((directory / 'index_meta.json').read_text())
        with np.load(directory / 'vectors.npz', allow_pickle=False) as index:
            self.vectors = index['vectors'].copy()
        if self.vectors.shape != (len(self.documents), self.meta['dimension']):
            raise RuntimeError('O índice da biblioteca está inconsistente.')
        if self.meta['model'] != 'gemini-embedding-001':
            raise RuntimeError('O modelo do índice é incompatível com a busca.')

    def count(self):
        return len(self.documents)

    def query(self, query_embeddings, n_results, include=None, where=None):
        q = np.asarray(query_embeddings[0], dtype=np.float32)
        norm = np.linalg.norm(q)
        if norm == 0 or not np.isfinite(q).all() or q.shape != (self.meta['dimension'],):
            raise RuntimeError('O serviço de pesquisa retornou dados inválidos.')
        q = q / norm
        indices = [i for i, d in enumerate(self.documents)
                   if not where or all(d['metadata'].get(k) == v for k, v in where.items())]
        scores = self.vectors[indices] @ q
        ordered = np.argsort(-scores, kind='stable')[:n_results]
        selected = [indices[int(i)] for i in ordered]
        return {
            'ids': [[self.documents[i]['id'] for i in selected]],
            'documents': [[self.documents[i]['text'] for i in selected]],
            'metadatas': [[self.documents[i]['metadata'] for i in selected]],
            'distances': [[float(1 - scores[int(i)]) for i in ordered]],
        }


def embed_query(text, key):
    with genai.Client(api_key=key, http_options={'timeout': 30000, 'retry_options': {'attempts': 1}}) as client:
        result = client.models.embed_content(
            model='gemini-embedding-001', contents=text,
            config=types.EmbedContentConfig(task_type='RETRIEVAL_QUERY', output_dimensionality=768),
        )
    return result.embeddings[0].values


def consume_quota(state, *, now=None, database=None, limits=None):
    """Limite global atômico por instância; sem armazenar perguntas ou identificadores."""
    now = time.time() if now is None else now
    day = int(now // 86400)
    limits = limits or (int(setting('GLOBAL_RPM', 3)), int(setting('GLOBAL_DAILY_LIMIT', 15)),
                        int(setting('SESSION_DAILY_LIMIT', 5)))
    rpm, daily, session_limit = limits
    if state.get('quota_day') != day:
        state['quota_day'], state['quota_used'] = day, 0
    if state.get('quota_used', 0) >= session_limit:
        return 'Esta sessão atingiu o limite de perguntas de hoje. O simulador continua disponível.'
    database = database or Path(tempfile.gettempdir()) / 'betwise_usage.sqlite3'
    with closing(sqlite3.connect(str(database), timeout=10)) as con, con:
        con.execute('CREATE TABLE IF NOT EXISTS attempts (at REAL NOT NULL)')
        con.execute('BEGIN IMMEDIATE')
        con.execute('DELETE FROM attempts WHERE at < ?', (day * 86400 - 60,))
        if con.execute('SELECT COUNT(*) FROM attempts WHERE at > ?', (now - 60,)).fetchone()[0] >= rpm:
            return 'Há muitas perguntas neste momento. Aguarde um minuto e tente novamente.'
        if con.execute('SELECT COUNT(*) FROM attempts WHERE at >= ?', (day * 86400,)).fetchone()[0] >= daily:
            return 'A demonstração atingiu o limite diário de perguntas. O simulador continua disponível.'
        con.execute('INSERT INTO attempts VALUES (?)', (now,))
    state['quota_used'] = state.get('quota_used', 0) + 1
    return None

