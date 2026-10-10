# 🏹 Arrowism

**Arrowism** é um minijogo desenvolvido em **Python com Pygame**, ambientado em um mundo medieval ameaçado por uma invasão alienígena. O protagonista é um herói que precisa enfrentar inimigos, superar salas cada vez mais difíceis e derrotar um chefe final.

O nome combina **Arrow** (*flecha*), sua arma principal, com **Heroism** (*heroísmo*), representando a missão do personagem de salvar seu mundo.

> Este README descreve a proposta do jogo. Algumas mecânicas e elementos visuais ainda podem estar em desenvolvimento e sujeitos a ajustes.

## 🎮 Jogabilidade

A proposta parte de um jogo de tiro e acrescenta combate em múltiplas direções, progressão por salas e uma batalha final contra um chefe.

- **Movimentação:** teclas `W`, `A`, `S` e `D`.
- **Combate:** o personagem começa com uma espada e uma flecha.
- **Flecha recuperável:** o jogador possui uma flecha principal que pode permanecer parada após ser lançada. Ao pressionar `Espaço`, pode chamá-la de volta, atingindo inimigos também no retorno.
- **Direções de ataque:** possibilidade de disparar em mais de uma direção.
- **Colisões e vidas:** o personagem começa com três espaços de vida e perde vida ao sofrer dano.
- **Salas e inimigos:** ondas limitadas de inimigos precisam ser vencidas para avançar.
- **Chefe final:** a última sala encerra a progressão com uma batalha contra um boss.

## ⚔️ Progressão e dificuldade

A dificuldade aumenta conforme o jogador limpa salas. Nas salas seguintes, os inimigos podem ganhar mais **vida, dano e velocidade**, além de aparecerem em maior quantidade ou em novas variedades.

Os valores exatos desses aumentos serão definidos durante o balanceamento. A progressão termina na sala do chefe final.

## ✨ Itens e melhorias

Entre os itens previstos estão:

| Item | Efeito planejado | Chance indicada na proposta |
| --- | --- | --- |
| **Tiro triplo** | Adiciona duas flechas menores ao lado da flecha principal, que desaparecem quando ela para. | 20% por sala |
| **Escudo** | Concede um ponto de proteção/vida adicional, recuperável ao limpar uma sala. | 20% por sala |
| **Vida extra** | Permite reviver uma vez por tentativa com um ponto de vida. | 10% por sala |
| **Tiro mais rápido** | Aumenta a velocidade da flecha na ida e na volta. | 25% por sala |

A proposta também prevê **corações** deixados por inimigos (10% de chance de drop), recuperação de um ponto de vida ao passar de sala e possíveis melhorias adicionais: **espada alongada, tiro distante, flecha mental e espada elemental**.

Como o jogador utiliza uma flecha recuperável, o ritmo de disparo depende também do momento em que ele decide trazê-la de volta. A velocidade da flecha poderá ser modificada por melhorias.

## 🖥️ Interface e apresentação

- **Menu inicial:** conceito visual de uma nave alienígena abduzindo o protagonista.
- **HUD:** corações para representar a vida, contador de salas concluídas e itens coletados durante a tentativa.
- **Transições:** tela escura suave com um pequeno OVNI atravessando a cena.
- **Game over:** representação do mundo dominado pelos alienígenas.

## 🎨 Direção artística

A identidade visual é inspirada em **Titan Souls** e **The Binding of Isaac**, com uma atmosfera de fantasia sombria, cores mais escuras e detalhes luminosos. *Titan Souls* é uma referência especial para a paleta de cores e a mecânica de combate.

## 🎵 Trilha sonora e efeitos

A ideia é usar **música eletrônica leve** fora dos combates e **música eletrônica mais intensa ou rock** durante as batalhas, além de efeitos sonoros para ataques, impactos e coleta de itens.

Referências musicais mencionadas na proposta:

- https://youtu.be/BhEnjxYLBYo
- https://www.youtube.com/watch?v=UtMRKYkqDf8
- https://www.youtube.com/watch?v=CzK3z8MLSpA

Esses links são referências de estilo; seu uso direto no jogo depende das permissões e licenças aplicáveis.

## 🛠️ Tecnologias

- **Python**
- **Pygame**
- **Programação Orientada a Objetos (POO)**
- **Git e GitHub** para colaboração

## 👥 Equipe

Projeto desenvolvido para a disciplina de **Programação Orientada a Objetos (POO)**, turma **1M**.

- Beatriz Almeida Lima
- Emilly Vitória Dutra Batista
- Isabela Nóbrega Rocha
- Júlia Dutra Fernandes
- Luis Felipe Torres Josue
- Pedro Diogo Paiva de Lima

## 💬 Nosso lema

> “Para resolver um erro, é só tornar ele uma feature.”
