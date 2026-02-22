# 💡 3 Formas de Setup - Escolha a Sua

Diferentes formas para diferentes usuários. Escolha aaquela com qual você se sente mais confortável!

---

## 🎯 Opção 1: Sem Terminal - Apenas Cliques ⭐ RECOMENDADO PARA INICIANTES

**Para quem:** Não gosta de terminal, quer simples e rápido

**Como usar:**

```
1️⃣ Clique duplo em:     setup.bat
   (Faz tudo automaticamente com perguntas)

2️⃣ Clique duplo em:     open_hub.bat
   (Abre painel de controle com botões gráficos)

3️⃣ Clique duplo em:     dashboard.bat
   (Abre o dashboard de monitoramento)
```

**Fluxo:**
- setup.bat pergunta "Quer PI AF real ou modo DEMO?" → você responde
- setup.bat pergunta "Quer gerar dados de teste?" → você responde
- setup.bat pergunta "Abrir dashboard agora?" → você responde
- Pronto! Tudo automático

**Vantagens:**
- ✅ Nenhum comando de terminal
- ✅ Perguntas simples em português
- ✅ Automático e rápido
- ✅ Melhor para iniciantes

**Desvantagens:**
- Requer Python 3.10+ instalado
- Windows apenas

---

## 💻 Opção 2: Com Terminal - Linhas Individuais ⭐ RECOMENDADO PARA QUEM TEM CONTROLE

**Para quem:** Familiarizado com terminal, quer executar passo a passo

**Como usar:**

1. Abra PowerShell ou CMD
2. Navegue até a pasta do projeto:
   ```bash
   cd C:\caminho\para\SafePlan
   ```
3. Execute os comandos um a um:

```bash
# 1. Configurar credenciais
python scripts/setup_credentials.py

# 2. Inicializar banco de dados
python scripts/init_db.py

# 3. Descobrir sensores (escolha um)
# Opção A: PI AF Real (requer acesso)
python scripts/discover_sensors_from_af.py

# Opção B: Modo DEMO (sem conexão)
python scripts/discover_sensors_from_af.py --demo

# 4. Importar sensores para banco
python scripts/import_sensors_from_buzios.py

# 5. Gerar dados de teste (opcional)
python scripts/create_sample_data.py

# 6. Abrir dashboard
streamlit run app/main.py
```

**Vantagens:**
- ✅ Mais controle
- ✅ Vê o que está acontecendo em cada passo
- ✅ Fácil debugar se houver problema
- ✅ Funciona em Windows, Mac e Linux

**Desvantagens:**
- Requer familiariarity com terminal
- Mais passos

---

## 🎨 Opção 3: Hub Gráfico - Interface Visual ⭐ RECOMENDADO PARA QUEM GOSTA DE UI

**Para quem:** Gosta de interface gráfica, quer botões e visual bonito

**Como usar:**

1. Abra PowerShell ou CMD
2. Navegue até o projeto:
   ```bash
   cd C:\caminho\para\SafePlan
   ```
3. Execute apenas este comando:
   ```bash
   streamlit run app/control_hub.py
   ```
4. Seu navegador abre com uma interface gráfica
5. Clique nos botões para fazer tudo

**O Hub oferece:**
- 🟢 **Status em tempo real** - Vê se está configurado/importado
- 🔐 **Configurar Credenciais** - Botão com interface segura
- 🗄️ **Gerenciar Banco** - Inicializar/verificar status
- 📡 **Gerenciar Sensores** - Descobrir/importar com botões
- ❓ **Ajuda Integrada** - Perguntas frequentes no hub
- 🔗 **Links Úteis** - Para documentação

**Vantagens:**
- ✅ Interface gráfica bonita
- ✅ Tudo em um lugar
- ✅ Status visual
- ✅ Sem terminal visível

**Desvantagens:**
- Requer Streamlit (já instalado)
- Usa porta 8501 do navegador

---

## 📊 Comparativo das 3 Opções

| Critério | Opção 1 (Batch) | Opção 2 (Terminal) | Opção 3 (Hub) |
|----------|--------|---------|-------|
| Nível de Dificuldade | ⭐ Muito Fácil | ⭐⭐⭐ Médio | ⭐⭐ Fácil |
| Tempo de Setup | ⏱️ 5-10 min | ⏱️ 10-15 min | ⏱️ 5 min |
| Interface | Texto | Texto | Gráfica |
| Controle | Baixo | Alto | Médio |
| Terminal Visível | ✅ Sim | ✅ Sim | ❌ Não |
| Funciona em Windows | ✅ Sim | ✅ Sim | ✅ Sim |
| Funciona em Mac/Linux | ❌ Não | ✅ Sim | ✅ Sim |
| Requer Python | ✅ Sim | ✅ Sim | ✅ Sim |

---

## 🎓 O Que Cada Opção Faz

Todas as 3 opções fazem exatamente a mesma coisa:

1. **Configura Credenciais**
   - Detecta seu username Windows
   - Pede sua senha de forma segura  
   - Salva no `.env`

2. **Inicializa Banco de Dados**
   - Cria tabelas necessárias
   - Pronto para receber sensores

3. **Descobre Sensores**
   - Conecta ao PI AF (ou modo DEMO)
   - Extrai 10 atributos de cada sensor
   - Salva em arquivo JSON

4. **Importa Sensores**
   - Lê o JSON
   - Cria registros no banco
   - Configura regras de alerta

5. **Gera Dados Teste** (Opcional)
   - Popula leituras de exemplo
   - Útil para testar dashboard

6. **Abre Dashboard**
   - Interface de monitoramento em tempo real
   - Visualiza sensores

---

## 🚀 Recomendações

### Para Iniciante Completo
→ **Use Opção 1 (setup.bat)**
- Mais simples
- Nenhum comando necessário
- Perguntas em português

### Para Usuário Técnico
→ **Use Opção 2 (Terminal)**
- Mais controle
- Fácil debugar
- Executa passo a passo

### Para Quem Quer Visual Bonito
→ **Use Opção 3 (Control Hub)**
- Interface gráfica
- Botões atraentes
- Status em tempo real

### Para Usar Tudo Junto Depois
→ Use **setup.bat** na primeira vez, depois **open_hub.bat** para abrir o hub

---

## ⚡ Em 30 Segundos

Escolha sua opção e execute:

**Opção 1:**
```
Clique duplo em setup.bat
Responda as perguntas
Pronto!
```

**Opção 2:**
```
python scripts/setup_credentials.py
python scripts/init_db.py
python scripts/discover_sensors_from_af.py --demo
python scripts/import_sensors_from_buzios.py
streamlit run app/main.py
```

**Opção 3:**
```
streamlit run app/control_hub.py
Clique nos botões
```

---

## ❓ Qual Escolher se Estou Indeciso?

**Primeira vez:**
→ Comece com **Opção 1 (setup.bat)**

**Depois, use o dashboard:**
→ Clique duplo em **dashboard.bat**

**Se quiser controle total depois:**
→ Aprenda **Opção 2 (Terminal)**

**Se quiser algo visual:**
→ Use **Opção 3 (Control Hub)**

---

## 📚 Próximos Passos

Depois que escolher e executar seu setup:

1. ✅ Credenciais configuradas
2. ✅ Banco inicializado
3. ✅ Sensores descobertos e importados
4. ✅ Dashboard pronto
5. 🚀 Comece a monitorar!

Vá para o [README.md](README.md) para entender mais sobre o projeto.
