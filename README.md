<div align="center">

# ✂️ Encurtador de URLs CLI

**Encurte links, copie para o clipboard e consulte seu histórico — tudo sem sair do terminal.**

![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![Typer](https://img.shields.io/badge/CLI-Typer-009688)
![Rich](https://img.shields.io/badge/UI-Rich-b266ff)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- Substitua pelo seu GIF ou print: grave com https://github.com/charmbracelet/vhs ou asciinema -->
![Demonstração](assets/demo.gif)

</div>

---

## ✨ Funcionalidades

- 🔗 Encurta URLs usando a API pública do **[is.gd](https://is.gd/apishorteningreference.php)** (sem chave de cadastro)
- ✅ Valida o formato da URL antes de qualquer requisição (e completa `https://` automaticamente)
- 📋 Copia o link encurtado para a área de transferência
- 🗂️ Salva o histórico local em JSON (URL original, URL encurtada e data)
- 📜 Lista o histórico em uma tabela colorida com **Rich**
- 🛡️ Tratamento de erros: URL inválida, sem internet, timeout, API fora do ar e histórico corrompido

## 🧰 Stack

| Camada | Tecnologia |
| --- | --- |
| CLI | [Typer](https://typer.tiangolo.com/) |
| HTTP | [Requests](https://requests.readthedocs.io/) |
| Terminal UI | [Rich](https://rich.readthedocs.io/) |
| Clipboard | [Pyperclip](https://github.com/asweigart/pyperclip) |
| Testes | [Pytest](https://pytest.org/) + `unittest.mock` |

## 🚀 Instalação

```bash
git clone https://github.com/SEU-USUARIO/encurtador-url-cli.git
cd encurtador-url-cli

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Opcional: instale o comando `encurtar` globalmente no ambiente virtual:

```bash
pip install -e .
```

> **Linux:** o `pyperclip` precisa de `xclip`, `xsel` ou `wl-clipboard`.
> Ex.: `sudo apt install xclip`. Sem isso, o link ainda é encurtado, mas não é copiado.

## 💻 Uso

> Sem instalar o pacote, troque `encurtar` por `python -m src`.

### Encurtar uma URL

```bash
$ encurtar shorten https://www.python.org/downloads/release/python-3120/
╭──────── ✅ Link encurtado ────────╮
│ https://is.gd/AbC123              │
│                                   │
│ 📋 Copiado para a área de         │
│ transferência!                    │
╰───────────────────────────────────╯
```

Opções: `--no-copy` desativa a cópia para o clipboard.

### Ver o histórico

```bash
$ encurtar history --limit 10
```

```
                     📜 Histórico de links
┏━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Data            ┃ URL original                ┃ URL encurtada      ┃
┡━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ 14/11/2026 10:42│ https://www.python.org/...  │ https://is.gd/AbC1 │
└───┴─────────────────┴─────────────────────────────┴────────────────────┘
```

### Limpar o histórico

```bash
encurtar clear        # pede confirmação
encurtar clear --yes  # sem confirmação
```

### Tratamento de erros

```bash
$ encurtar shorten "isso não é url"
╭─ ❌ URL inválida ─────────────────╮
│ A URL não pode conter espaços.    │
╰───────────────────────────────────╯
```

## 🗂️ Estrutura do projeto

```
encurtador-url-cli/
├── src/
│   ├── api.py          # Integração com a API do is.gd
│   ├── cli.py          # Comandos Typer + saída Rich
│   ├── clipboard.py    # Acesso ao clipboard
│   ├── history.py      # Histórico em JSON
│   └── validators.py   # Validação/normalização de URLs
├── tests/              # Testes com pytest e mocks
├── requirements.txt
└── pyproject.toml
```

O histórico fica em `~/.encurtador-url/history.json`. Para mudar o local, defina
a variável de ambiente `ENCURTADOR_HISTORY_FILE`.

## 🧪 Testes

```bash
pip install -r requirements-dev.txt
pytest
```

As chamadas HTTP e o clipboard são simulados com mocks, então os testes rodam
offline e não dependem da API.

## 🗺️ Próximos passos

- [ ] Suporte a alias personalizado (`--alias`)
- [ ] Exportar histórico para CSV
- [ ] Escolha de provedor (`--provider tinyurl|isgd`)
- [ ] CI com GitHub Actions

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).

---

<div align="center">Feito com 🐍 por <a href="https://github.com/SEU-USUARIO">wx</a></div>
