# Manipulando E-mails no Apache NiFi 2.0 com Python

<p align="center">
  <img src="https://raw.githubusercontent.com/Renatoelho/nifi-python-email-processadores/main/imagens/banner.png" alt="Banner do Projeto">
</p>

Este projeto demonstra como implementar dois processadores personalizados utilizando **Python** no **Apache NiFi 2.0**, com foco na manipulação de **e-mails** via servidor IMAP. A ideia é extrair e-mails do servidor conforme vão chegando via processador **ConsumeIMAP**, transformá-los em JSON estruturado, incluindo opcionalmente os anexos em base64, e depois reverter esse conteúdo dos anexos originais para usos diversos, como análise e compreensão com **LLMs/GenIA** por exemplo.

## Apresentação em Vídeo

[... Em desenvolvimento (Aproveite e acesse meu canal no YouTube, lá tem muito conteúdo interessante.) ...](https://youtube.com/@renato-coelho)

<!-- 
<p align="center">
  <a href="https://youtu.be/xxxxxxxxx" target="_blank"><img src="imagens/thumbnail/thumbnail-emails-nifi-python.png" alt="Vídeo de apresentação"></a>
</p>

![YouTube Video Views](https://img.shields.io/youtube/views/xxxxxxxxx)
![YouTube Video Likes](https://img.shields.io/youtube/likes/xxxxxxxxx)
-->

## Requisitos

+ ![Docker](https://img.shields.io/badge/Docker-27.4.1-E3E3E3)
+ ![Docker-compose](https://img.shields.io/badge/Docker--compose-1.25.0-E3E3E3)
+ ![Git](https://img.shields.io/badge/Git-2.25.1%2B-E3E3E3)
+ ![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%2B-E3E3E3)

## 📨 ConvertEmailToJSON

Este processador foi criado para ser utilizado dentro do Apache NiFi 2.0 e tem como função converter e-mails capturados em seu formato bruto (.eml) em arquivos JSON estruturados. Ele extrai os seguintes dados principais:

+ Remetente (From)
+ Destinatários (To, Cc, Bcc)
+ Assunto
+ Data da mensagem
+ Corpo do e-mail (texto simples ou HTML)
+ Anexos (opcional)

### Destaques:

+ Os anexos são incluídos no JSON como objetos contendo metadados (nome e tipo) e o conteúdo em base64, facilitando o transporte e análise posterior.

+ Ideal para cenários onde é necessário processar os anexos posteriormente, como envio para LLMs ou arquivamento inteligente.

+ Possui uma propriedade configurável para incluir ou não os anexos no JSON ```Adiciona anexo(s) ao Json```.

Exemplo de Json Estruturado a partir de uma e-mail

```json
{
  "assunto": "Teste conversão de Anexos",
  "de": "*********@origem.com",
  "para": "*********@destino.com.br",
  "cc": "",
  "data": "2025-04-24 23:53:03",
  "mensagem_id": "<**********@mail.com>",
  "resposta_para": "",
  "conteudo": {
    "text/plain": "Segue em anexo.",
    "text/html": "<div>Segue em anexo.</div>"
  },
  "anexos": [
    {
      "nome": "teste.txt",
      "tipo": "text/plain",
      "conteudo_base64": "********"
    }
  ]
}
```

## 📎 EmailJSONToAttachment

Este processador faz o caminho inverso: ele recebe os arquivos JSON gerados pelo ConvertEmailToJSON.py (após passar por um SplitJson no array de anexos), e converte novamente os anexos que estão codificados em base64 de volta para seus arquivos originais.

### Funcionalidade:

+ Recria um flowfile para cada anexo.

+ O conteúdo é decodificado do **base64** e o arquivo original é restaurado com os metadados preservados.

+ Permite o reaproveitamento do conteúdo extraído do e-mail, seja para armazenamento, análise ou envio para outros sistemas.

### Observações importantes:

+ Exige que um SplitJson seja aplicado antes, para que cada flowfile contenha apenas um anexo por vez.

+ A propriedade ```Max String Length``` do **SplitJson** deve ser configurada para pelo menos **1024 MB**, garantindo que o conteúdo base64 completo do anexo não seja truncado.

## Deploy 

### Clonando e Acessando o Repositório do Projeto

```bash
git clone https://github.com/Renatoelho/nifi-python-email-processadores.git nifi-python-email-processadores
```

```bash
cd nifi-python-email-processadores
```

### Ativando a Infra no Docker via Docker Compose

```bash
docker compose -p nifi-python-email -f docker-compose.yaml up -d
```

### Implementação dos processadores

```bash
docker cp ConvertEmailToJSON/ apache-nifi:/opt/nifi/nifi-current/python_extensions
```

```bash
docker logs -f apache-nifi | grep -Ei ConvertEmailToJSON
```

```bash
docker cp EmailJSONToAttachment.py apache-nifi:/opt/nifi/nifi-current/python_extensions
```

```bash
docker logs -f apache-nifi | grep -Ei EmailJSONToAttachment
```

## Credenciais de Acessos

<details>
<summary>Clique aqui e veja as Credenciais</summary>
<br>

### Apache Nifi

- **Url**: https://localhost:8443/nifi/
- **Usuário**: nifi
- **Senha**: HGd15bvfv8744ghbdhgdv7895agqERAo

### MySQL

- **Host Externo**: localhost
- **Host Interno**: mysql
- **Usuário**: root
- **Senha**: W45uE75hQ15Oa
- **Porta**: 3306

### Elasticsearch

- **Ulr Externa**: http://localhost:9200
- **Url Interna**: http://elasticsearch:9200
- **Usuário**: elastic
- **Senha**: nY5AQz37ZZIfMev9nY5AQz37ZZIfMev9


### MinIO/S3

- **Url**: http://localhost:9001/login
- **Usuário**: admin
- **Senha**: eO3RNPcKgWInlzPJuI08

- **Url API Interna**: http://minio-s3:9000
- **Porta API Interna**: 9000


### Kibana

- **Url**: http://localhost:5601/login
- **Usuário**: elastic
- **Senha**: nY5AQz37ZZIfMev9nY5AQz37ZZIfMev9


</details>

## Referências

Multiple flowfiles as output for Python Processors, **issues.apache.org** Disponível em: <https://issues.apache.org/jira/browse/NIFI-13402>. Acesso em: 17 Abr. 2025.

NiFi Python Developer’s Guide, **nifi.apache.org** Disponível em: <https://nifi.apache.org/nifi-docs/python-developer-guide.html>. Acesso em: 17 Abr. 2025.

python extension generate multiple flowfiles from bytes input, **Cloudera Community** Disponível em: <https://community.cloudera.com/t5/Support-Questions/python-extension-generate-multiple-flowfiles-from-bytes/m-p/383095>. Acesso em: 17 Abr. 2025.

nifi-python-extensions, **Apache NiFi Python Extensions** Disponível em: <https://github.com/apache/nifi-python-extensions>. Acesso em: 17 Abr. 2025.
