-- Arquivo: siac_datamart_ddl.sql

-- 1. DIMENSÕES

-- Dim_Tempo: Para analisar trabalhos por período de submissão/publicação.
CREATE TABLE Dim_Tempo (
    id_tempo SERIAL PRIMARY KEY,
    data_completa DATE NOT NULL UNIQUE,
    ano SMALLINT NOT NULL,
    semestre SMALLINT,
    trimestre SMALLINT,
    mes SMALLINT NOT NULL,
    nome_mes VARCHAR(20),
    dia_semana SMALLINT NOT NULL,
    nome_dia_semana VARCHAR(20)
);

-- Dim_Local: Para analisar afiliações e procedência geográfica.
CREATE TABLE Dim_Local (
    id_local SERIAL PRIMARY KEY,
    nome_instituicao VARCHAR(255) NOT NULL,
    sigla_instituicao VARCHAR(50),
    departamento VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(100),
    pais VARCHAR(100)
);

-- Dim_Pessoa: Para analisar os autores e co-autores.
CREATE TABLE Dim_Pessoa (
    id_pessoa SERIAL PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    primeiro_nome VARCHAR(100),
    sobrenome VARCHAR(100),
    orcid VARCHAR(50) UNIQUE,
    email VARCHAR(255)
);

-- Dim_Trabalho: Descreve o item de conteúdo (o Resumo/Artigo).
CREATE TABLE Dim_Trabalho (
    id_trabalho SERIAL PRIMARY KEY,
    titulo VARCHAR(512) NOT NULL,
    tipo_trabalho VARCHAR(50), 
    area_conhecimento VARCHAR(255),
    numero_palavras INTEGER,
    numero_autores INTEGER
);


-- 2. TABELA FATO

-- Fato_Resumo: Liga todas as dimensões e armazena métricas.
CREATE TABLE Fato_Resumo (
    id_fato SERIAL PRIMARY KEY,
    
    -- Chaves Estrangeiras (Links para as Dimensões)
    fk_id_tempo INTEGER REFERENCES Dim_Tempo(id_tempo),
    fk_id_trabalho INTEGER REFERENCES Dim_Trabalho(id_trabalho),
    fk_id_local_instituicao INTEGER REFERENCES Dim_Local(id_local), 
    
    -- Colunas para representar o relacionamento 
    fk_id_autor_principal INTEGER REFERENCES Dim_Pessoa(id_pessoa), 

    -- Métricas (O que será analisado/medido)
    contagem_resumo INTEGER DEFAULT 1 NOT NULL, 
    status_aprovacao VARCHAR(50),
    nota_media_avaliacao NUMERIC(3, 1) 
);