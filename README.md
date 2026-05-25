# SalomoneUI

A plataforma SalomoneUI local e portátil 100% autossuficiente.
Sem necessidade de internet, sem nuvem, todos os seus dados e banco de dados SQLite ficam armazenados exclusivamente na sua máquina ou no seu pendrive.

## ⬇️ Como Baixar os Executáveis

O GitHub não permite colocar arquivos maiores que 100MB diretamente no código-fonte, portanto, os aplicativos compilados estão salvos de forma oficial na aba **Releases** do repositório.

1. Acesse a aba [Releases](../../releases) deste repositório (no menu à direita no GitHub).
2. Na última versão (SalomoneUI v1.9.25), você verá dois arquivos para baixar:
   - **AionUi-1.9.25-Portable.exe** (Versão Portátil para Pendrive/HD Externo)
   - **AionUi-1.9.25-Setup.exe** (Instalador Padrão do Windows)

---

## 🚀 Como Executar

### Opção 1: Versão Portátil (Recomendada para mobilidade)
1. Coloque o arquivo `AionUi-1.9.25-Portable.exe` na pasta desejada (Ex: dentro do seu Pendrive ou em uma pasta na Área de Trabalho).
2. Dê um duplo clique para abrir.
3. Ele criará instantaneamente uma pasta secreta chamada `salomoneui-data` **ao lado** do executável. O seu banco de dados e todos os documentos ficarão armazenados e protegidos nessa pasta, viajando com você para qualquer lugar.

### Opção 2: Instalador Local (Instalação fixa no PC)
1. Dê um duplo clique em `AionUi-1.9.25-Setup.exe`.
2. A instalação ocorrerá e um atalho será criado. O programa abrirá automaticamente e salvará seus dados no seu perfil de usuário do Windows (`AppData`).

---

## ⚠️ Solução de Problemas (Troubleshooting)

**"Eu tentei abrir no computador do trabalho e o aplicativo sequer abriu (nenhuma tela, nenhum erro)."**

Computadores corporativos possuem políticas de TI extremamente rígidas que silenciosamente bloqueiam aplicativos que não são reconhecidos pelo sistema corporativo. Se o aplicativo simplesmente não abre, verifique os seguintes passos:

1. **Bloqueio do Windows (SmartScreen):**
   - Clique com o botão direito no arquivo `.exe` baixado.
   - Selecione **Propriedades**.
   - Na aba "Geral", na parte inferior, se houver uma caixa marcando **Desbloquear** (Unblock), marque-a e clique em Aplicar. (O Windows bloqueia por padrão arquivos baixados da internet ou transferidos por pendrive).

2. **Bloqueio de Antivírus Corporativo:**
   - Softwares como CrowdStrike, McAfee ou Windows Defender corporativo costumam bloquear executáveis `.exe` portáteis sem avisar o usuário. Tente colocar a pasta do executável nas exclusões do seu antivírus ou converse com a TI caso o computador bloqueie softwares de terceiros.

3. **Permissões de Escrita:**
   - A versão Portátil *precisa* ter permissão para criar a pasta `salomoneui-data` no diretório onde está localizada. Se você a colocou no "Disco C:\" na raiz ou em uma pasta de sistema protegida, ela não conseguirá escrever os arquivos e falhará silenciosamente. Coloque o arquivo na pasta "Documentos" ou na raiz do seu próprio Pendrive.
