"""Coordena uma tentativa completa, do primeiro pátio ao chefe final."""

import random
import pygame
from apresentacao import CenarioSala, HUD, Transicao
from armas import Espada, Flecha
from audio import Audio
from configuracoes import LARGURA, ALTURA, TOTAL_SALAS
from entidades import Jogador
from inimigos import TIPOS_INIMIGOS
from itens import Coletavel, ITENS
from salas import Sala
from sprites import RecursosSprites


class Jogo:
    def __init__(self, recursos=None, audio=None, tamanho=(LARGURA, ALTURA), rng=None):
        self.recursos = recursos if recursos is not None else RecursosSprites()
        self.audio = audio if audio is not None else Audio(ativo=False)
        self.rng = rng if rng is not None else random.Random()
        self.tamanho = tamanho
        self.cenario = CenarioSala(tamanho)
        self.hud = HUD(tamanho, self.recursos)
        self.jogador = Jogador(self.cenario.limites.centerx, self.cenario.limites.bottom - 70, self.recursos)
        self.inimigos = pygame.sprite.Group()
        self.projeteis = pygame.sprite.Group()
        self.coletaveis = []
        self.flecha = Flecha(self.recursos)
        self.espada = Espada()
        self.pontos = 0
        self.salas_concluidas = 0
        self.tempo = 0
        self.pausado = False
        self.mensagem = ""
        self.mensagem_tempo = 0
        self.ultimo_quadro = pygame.time.get_ticks()
        self.transicao = None
        self.acao_final = None
        self._preparar_sala(1)
        self.avisar("Setas: flecha · Espaço: trazer de volta · J: espada", 4500)
        self.transicao = Transicao(tamanho, "Sala 1 · O pátio esquecido")

    def avisar(self, mensagem, duracao=3300):
        self.mensagem = mensagem
        self.mensagem_tempo = duracao

    def _preparar_sala(self, numero):
        self.inimigos.empty()
        self.projeteis.empty()
        self.coletaveis.clear()
        self.flecha.reiniciar()
        self.espada = Espada()
        self.cenario.preparar(numero)
        self.sala = Sala(numero, self.cenario.limites, self.rng)
        self.recompensa_entregue = False
        self.jogador.posicao.update(self.cenario.limites.centerx, self.cenario.limites.bottom - 70)
        self.jogador.rect.center = self.jogador.posicao
        self.jogador.tempo_ataque = 0
        if numero > 1:
            self.jogador.curar(1)
        self.audio.ambiente("chefe" if numero == TOTAL_SALAS else "combate")

    def _avancar(self):
        if self.sala.concluida and self.sala.numero < TOTAL_SALAS:
            if self.jogador.posicao.distance_to(self.cenario.portal_saida) <= 80:
                numero = self.sala.numero + 1
                self.transicao = Transicao(self.tamanho, f"Sala {numero} · {Sala.NOMES[numero - 1]}",
                                            lambda: self._preparar_sala(numero))
            else:
                self.avisar("Vá ao portal no alto da sala e pressione E.")

    def _espada(self, direcao=None):
        if self.espada.atacar(self.jogador, direcao):
            self.audio.tocar("espada")

    def _disparar(self, direcao):
        if self.flecha.disparar(self.jogador, direcao):
            self.audio.tocar("flecha")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.pausado = not self.pausado
            self.audio.ambiente("calma" if self.pausado or self.sala.concluida else
                                "chefe" if self.sala.numero == TOTAL_SALAS else "combate")
            return None
        if self.pausado:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return "jogar"
                if evento.key == pygame.K_q:
                    return "menu"
            return None
        if self.transicao or self.jogador.vida <= 0:
            return None
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and self.flecha.chamar():
                self.audio.tocar("retorno")
            elif evento.key == pygame.K_j:
                self._espada()
            elif evento.key == pygame.K_e:
                self._avancar()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            direcao = pygame.Vector2(evento.pos) - self.jogador.posicao
            if evento.button == 1:
                self._espada(direcao)
            elif evento.button == 3:
                self._disparar(direcao)
        return None

    def _registrar_mortes(self):
        for inimigo in self.inimigos:
            if inimigo.morrendo and not inimigo.recompensado:
                inimigo.recompensado = True
                self.pontos += inimigo.valor
                if self.rng.random() < .10:
                    self.coletaveis.append(Coletavel("coracao", inimigo.posicao, self.recursos))

    def _concluir_sala(self):
        self.recompensa_entregue = True
        self.salas_concluidas += 1
        self.pontos += 50 * self.sala.numero
        self.jogador.recarregar_escudo()
        self.projeteis.empty()
        self.audio.tocar("sala")
        self.audio.ambiente("calma")
        if self.sala.numero < TOTAL_SALAS:
            codigos = self.jogador.inventario.sortear_recompensas(self.rng)
            centro = self.cenario.limites.center
            for indice, codigo in enumerate(codigos):
                x = centro[0] + (indice - (len(codigos) - 1) / 2) * 140
                self.coletaveis.append(Coletavel(codigo, (x, centro[1]), self.recursos))
            self.avisar("Sala limpa! Recolha os itens e use E junto ao portal.", 6500)

    def atualizar(self, dt=None):
        agora = pygame.time.get_ticks()
        if dt is None:
            dt = min(50, agora - self.ultimo_quadro)
        self.ultimo_quadro = agora
        if self.pausado:
            return None
        if self.transicao:
            self.transicao.atualizar(dt)
            if self.transicao.finalizada:
                self.transicao = None
                if self.acao_final:
                    return self.acao_final
            return None
        teclas = pygame.key.get_pressed()
        if self.jogador.vida <= 0:
            self.jogador.atualizar(dt, teclas, self.cenario.limites)
            return "derrota" if self.jogador.morte_finalizada else None

        self.tempo += dt
        self.mensagem_tempo = max(0, self.mensagem_tempo - dt)
        self.jogador.atualizar(dt, teclas, self.cenario.limites)
        direcao = pygame.Vector2(int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT]),
                                 int(teclas[pygame.K_DOWN]) - int(teclas[pygame.K_UP]))
        if direcao.length_squared():
            self._disparar(direcao)
        if teclas[pygame.K_j]:
            self._espada()

        vida_anterior = sum(i.vida for i in self.inimigos)
        self.flecha.atualizar(dt, self.jogador, self.inimigos, self.cenario.limites)
        self.espada.atualizar(dt, self.jogador, self.inimigos)
        self._registrar_mortes()
        for inimigo in list(self.inimigos):
            inimigo.atualizar(dt, self.jogador, self.cenario.limites, self.projeteis)
        self._registrar_mortes()
        if sum(i.vida for i in self.inimigos) < vida_anterior:
            self.audio.tocar("impacto")

        for projetil in list(self.projeteis):
            projetil.atualizar(dt, self.cenario.limites)
            if projetil.atingiu(self.jogador):
                if self.jogador.sofrer_dano(projetil.dano):
                    self.audio.tocar("dano")
                projetil.kill()
        for inimigo in self.inimigos:
            if not inimigo.morrendo and inimigo.hitbox.colliderect(self.jogador.hitbox):
                if self.jogador.sofrer_dano(inimigo.dano):
                    self.audio.tocar("dano")
        if self.jogador.reviver_pendente:
            self.jogador.reviver_pendente = False
            self.avisar("Vida extra consumida! Você voltou com um coração.", 4500)
            self.audio.tocar("coleta")
        if self.jogador.vida <= 0:
            return None

        for coletavel in self.coletaveis[:]:
            coletavel.atualizar(dt)
            if coletavel.rect.colliderect(self.jogador.hitbox) and coletavel.coletar(self.jogador):
                self.coletaveis.remove(coletavel)
                self.audio.tocar("coleta")
                if coletavel.codigo in ITENS:
                    item = ITENS[coletavel.codigo]
                    self.avisar(f"{item.nome}: {item.descricao}", 4800)

        vivos = sum(not i.morrendo for i in self.inimigos)
        novos = self.sala.atualizar(dt, vivos, self.jogador)
        for tipo, posicao in novos:
            self.inimigos.add(TIPOS_INIMIGOS[tipo](posicao, self.sala.numero, self.recursos))
        if self.sala.concluida and not self.recompensa_entregue:
            self._concluir_sala()
        if self.sala.concluida and self.sala.numero == TOTAL_SALAS and not self.inimigos:
            self.acao_final = "vitoria"
            self.transicao = Transicao(self.tamanho, "A invasão terminou. O reino resistiu.")
        return None

    def desenhar(self, tela):
        self.cenario.desenhar(tela, self.sala, self.tempo)
        for portal in self.sala.pendentes:
            portal.desenhar(tela)
        for coletavel in self.coletaveis:
            mostrar = self.sala.concluida or coletavel.posicao.distance_to(self.jogador.posicao) < 95
            coletavel.desenhar(tela, mostrar)
        for inimigo in sorted(self.inimigos, key=lambda i: i.rect.bottom):
            inimigo.desenhar(tela)
        self.projeteis.draw(tela)
        self.jogador.desenhar(tela)
        self.flecha.desenhar(tela)
        self.espada.desenhar(tela, self.jogador)
        self.hud.desenhar(tela, self)
        if self.transicao and not self.pausado:
            self.transicao.desenhar(tela)


def iniciar(tela):
    """Entrada alternativa para executar uma partida diretamente."""
    from main import Arrowism
    aplicacao = Arrowism(tela)
    aplicacao.iniciar_partida()
    aplicacao.executar()


if __name__ == "__main__":
    pygame.init()
    iniciar(pygame.display.set_mode((LARGURA, ALTURA)))
