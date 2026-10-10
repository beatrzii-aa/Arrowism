# 🏹 Arrowism

**Arrowism** é um minijogo em **Python com Pygame**, desenvolvido com **Programação Orientada a Objetos**, ambientado em um reino medieval invadido por alienígenas. Sobreviva a cinco salas com ondas de inimigos e enfrente o chefe na sexta sala.

O jogo abre em uma **janela de 1024 × 768**, sem tela cheia. O tamanho está em `Códigos/configuracoes.py`.

## ▶️ Como executar

Use Python **3.11 a 3.13**. A implementação foi validada com Python 3.13 e Pygame 2.6.1.

Na pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente com `source .venv/bin/activate` no Linux/macOS ou `.venv\Scripts\Activate.ps1` no PowerShell. Depois:

```bash
python -m pip install -r requirements.txt
python "Códigos/main.py"
```

Com o ambiente já existente neste projeto, também é possível executar diretamente:

```bash
.venv/bin/python "Códigos/main.py"
```

## 🎮 Controles e combate

| Ação | Controle |
| --- | --- |
| Mover | `W`, `A`, `S`, `D` |
| Disparar a flecha | Setas direcionais; combine duas para disparar na diagonal |
| Mirar e disparar com o mouse | Botão direito |
| Chamar a flecha de volta | `Espaço` |
| Usar a espada | `J`, na direção em que o personagem olha |
| Mirar e usar a espada com o mouse | Botão esquerdo |
| Avançar depois de limpar a sala | `E`, próximo ao portal no alto da arena |
| Pausar/continuar | `Esc` |
| Reiniciar durante a pausa | `R` |
| Voltar ao menu durante a pausa | `Q` |
| Ativar/silenciar música e efeitos | `M` |

No menu, `Enter` começa a partida e `Esc` sai. Nas telas de derrota e vitória, `Enter` tenta novamente e `Esc` volta ao menu. O jogo também pausa ao perder o foco da janela.

- O herói começa com **três corações, uma espada e uma flecha**.
- A flecha atravessa inimigos, para ao alcançar a parede ou seu limite de distância e permanece no cenário até ser chamada. Não é possível lançar outra enquanto ela não retornar.
- `Espaço` pode chamar a flecha ainda durante o voo. Ela acompanha a posição atual do jogador e também causa dano no retorno.
- Cada flecha causa **um ponto de dano por inimigo na ida e outro na volta**. Ficar sobre um alvo não causa dano repetido.
- A espada causa **dois pontos de dano** em um arco à frente do jogador, com intervalo de **0,43 segundo** entre ataques.
- Após sofrer um golpe, o jogador fica protegido por **1,1 segundo**, com indicação visual. A movimentação e as animações usam tempo decorrido; andar na diagonal não aumenta a velocidade.

## ⚔️ Salas, inimigos e chefe

A campanha tem **seis salas**, com este balanceamento inicial:

| Sala | Nome | Ondas | Inimigos por onda | Novidade |
| --- | --- | --- | --- | --- |
| 1 | O pátio esquecido | 2 | 3 | Batedores perseguem o jogador |
| 2 | Muralhas em silêncio | 2 | 4 | Sentinelas atiram à distância |
| 3 | O jardim corrompido | 2 | 5 | Caçadores avisam antes de avançar rapidamente |
| 4 | A fortaleza ocupada | 2 | 6 | Guardiões resistem mais e causam dois pontos de dano |
| 5 | O último bastião | 2 | 7 | Mistura das quatro variedades |
| 6 | O coração da invasão | 1 | 1 chefe | Arconte do Vazio |

A vida e a velocidade dos inimigos aumentam com o número da sala. Guardiões são maiores e mais lentos. Os pontos luminosos na arena avisam onde os próximos inimigos surgirão.

O **Arconte do Vazio** possui **52 pontos de vida** e causa dois pontos de dano por contato. Ele dispara padrões circulares com aviso visual. Ao perder metade da vida, passa para a segunda fase, fica mais rápido e acrescenta disparos direcionados. Derrotá-lo encerra a campanha com uma tela de vitória.

As ondas são limitadas: é preciso derrotar todos os inimigos. Ao limpar uma sala, o portal se abre e os itens sorteados aparecem no centro. Recolha-os antes de avançar; objetos deixados na sala não acompanham o jogador. A passagem para a próxima sala recupera **um coração**, sem ultrapassar o máximo.

## ✨ Itens e melhorias

O sorteio ocorre ao limpar cada sala anterior ao chefe, com uma rolagem independente por item. Portanto, uma sala pode conceder vários itens ou nenhum. Cada melhoria pode ser adquirida uma única vez por tentativa.

| Item | Efeito | Chance por sala |
| --- | --- | --- |
| **Tiro triplo** | Duas flechas menores acompanham a principal e desaparecem quando ela para. | 20% |
| **Escudo** | Absorve um golpe inteiro e recarrega ao limpar uma sala. | 20% |
| **Vida extra** | Revive uma única vez na tentativa, com um coração e proteção temporária. | 10% |
| **Tiro mais rápido** | Aumenta a velocidade da flecha em 35%, tanto na ida quanto na volta. | 25% |

Há ainda **25% de chance por sala** de aparecer uma das melhorias adicionais ainda não adquiridas:

- **Espada alongada:** aumenta o alcance da espada de 72 para 112 pixels.
- **Tiro distante:** aumenta o alcance da flecha de 380 para 580 pixels.
- **Flecha mental:** curva o disparo na ida em direção a inimigos a até 240 pixels de distância.
- **Espada elemental:** incendeia os alvos, causando um ponto de dano por segundo durante três segundos; novos golpes renovam a duração.

Cada inimigo derrotado tem **10% de chance de deixar um coração**. Corações só são coletados quando há vida a recuperar. A vida extra, depois de usada, permanece indicada no HUD e não pode ser obtida novamente na mesma tentativa.

As velocidades básicas da flecha são 600 pixels/s na ida e 760 pixels/s na volta. O ritmo dos disparos depende da recuperação da flecha e do momento em que o jogador decide chamá-la.

## 🖥️ Interface e apresentação

- **Menu inicial:** OVNI animado abduzindo o protagonista sobre as muralhas.
- **HUD:** corações, escudo, pontuação, sala atual, ondas, salas concluídas, melhorias e estado da flecha.
- **Arena:** piso de pedra, muralhas escuras, runas luminosas e portais.
- **Transições:** escurecimento suave com um pequeno OVNI atravessando a cena.
- **Derrota:** animação de morte seguida do mundo dominado pelos alienígenas.
- **Vitória:** reino salvo, pontuação e opção de jogar novamente.

A direção artística segue a proposta de fantasia sombria com cores escuras e detalhes luminosos, inspirada em **Titan Souls** e **The Binding of Isaac**.

As animações do personagem e dos aliens usam a folha `Sprites/Personagem e Alien.jpg`. O carregador recorta os quadros e remove o fundo pelas bordas; como o original é JPG, podem restar marcas de compressão. A flecha usa a transparência do arquivo `Sprites/ARCO E FLECHA.pixil`. Os originais, incluindo o projeto completo de animação do arco, permanecem preservados.

## 🎵 Trilha sonora e efeitos

O jogo sintetiza **música e efeitos originais** localmente com Pygame, sem precisar baixar arquivos:

- Eletrônica leve no menu, na pausa e após limpar salas.
- Batida mais intensa durante o combate e uma variação mais rápida no chefe.
- Efeitos para disparo, espada, retorno da flecha, impactos, dano, coleta e vitória.

O jogo continua funcionando se nenhum dispositivo de áudio estiver disponível. Use `M` para silenciar ou reativar o som.

Referências de estilo da proposta original, não incorporadas como gravações ao jogo:

- https://youtu.be/BhEnjxYLBYo
- https://www.youtube.com/watch?v=UtMRKYkqDf8
- https://www.youtube.com/watch?v=CzK3z8MLSpA

## 🛠️ Organização em POO

| Arquivo em `Códigos/` | Responsabilidade |
| --- | --- |
| `main.py` | Classe `Arrowism`: janela, áudio e troca de telas |
| `jogo_tiro.py` | Classe `Jogo`: coordena cada tentativa |
| `entidades.py` | Entidades, animação e estado do jogador |
| `armas.py` | Flecha recuperável, espada e projéteis alienígenas |
| `inimigos.py` | Inimigos especializados e chefe por herança |
| `salas.py` | Ondas finitas e avisos de surgimento |
| `itens.py` | Inventário, chances e objetos coletáveis |
| `sprites.py` | Recortes da folha, leitura de Pixilart e animações |
| `apresentacao.py` | Cenário, HUD, OVNI e transições |
| `audio.py` | Síntese, reprodução e controle de som |
| `menu.py`, `tela_derrota.py`, `tela_vitoria.py` | Telas e botões |
| `configuracoes.py` | Janela, FPS, vida inicial e quantidade de salas |

Os recursos gráficos são compartilhados entre entidades e tentativas; inventário, vida e progresso pertencem a cada partida. Os parâmetros atuais são um ponto de partida para ajustes de dificuldade após partidas reais.

## 🧪 Verificação

Com o ambiente virtual ativo:

```bash
python -m unittest discover -s tests -v
```

Os testes usam os drivers de vídeo e áudio de teste do SDL. Verificam combate, retorno da flecha, efeitos dos itens, probabilidades, pausa, animação de morte, áudio, reinício e progressão pelas seis salas até a vitória. A simulação de campanha elimina inimigos de forma controlada para verificar o fluxo; não substitui uma avaliação humana de dificuldade.

## 👥 Equipe

Projeto desenvolvido para a disciplina de **Programação Orientada a Objetos (POO)**, turma **1M**.

- Beatriz Almeida Lima
- Emilly Vitória Dutra Batista
- Isabela Nóbrega Rocha
- Júlia Dutra Fernandes
- Luis Felipe Torres Josue
- Pedro Diogo Paiva de Lima
