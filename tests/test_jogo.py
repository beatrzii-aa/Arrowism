"""Regressões das regras da campanha. Executar: python -m unittest discover -s tests -v."""

import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import random
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Códigos'))
import pygame
from apresentacao import Transicao
from armas import Flecha, ProjetilAlien
from audio import Audio
from configuracoes import TOTAL_SALAS
from inimigos import Alien, AlienBruto, AlienAtirador, AlienCorredor, Chefe
from itens import Coletavel, Inventario, ITENS
from jogo_tiro import Jogo
from main import Arrowism
from menu import MenuInicial
from sprites import RecursosSprites
from tela_derrota import TelaDerrota
from tela_vitoria import TelaVitoria


class SorteioFixo:
    def __init__(self, valor):
        self.valor = valor

    def random(self):
        return self.valor

    def choice(self, valores):
        return valores[0]


class RegrasDoJogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.init()
        cls.tela = pygame.display.set_mode((1024, 768))
        cls.recursos = RecursosSprites()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.jogo = Jogo(self.recursos, Audio(ativo=False), rng=random.Random(7))
        self.jogo.transicao = None
        self.jogo.sala.espera = 1000000
        self.jogador = self.jogo.jogador
        self.posicionar(300, 400)
        self.teclas = patch('pygame.key.get_pressed', return_value=defaultdict(bool))
        self.teclas.start()
        self.addCleanup(self.teclas.stop)

    def posicionar(self, x, y):
        self.jogador.posicao.update(x, y)
        self.jogador.rect.center = (x, y)

    def inimigo(self, x, y, vida=10):
        inimigo = AlienBruto((x, y), 4, self.recursos)
        inimigo.vida = inimigo.vida_maxima = vida
        inimigo.velocidade = 0
        self.jogo.inimigos.add(inimigo)
        return inimigo

    def avancar(self, ms):
        for _ in range(round(ms / 20)):
            self.jogo.atualizar(20)

    def test_tres_coracoes_e_uma_flecha(self):
        self.assertEqual(self.jogador.vida, 3)
        self.assertTrue(self.jogo.flecha.disparar(self.jogador, (1, 0)))
        self.assertFalse(self.jogo.flecha.disparar(self.jogador, (0, 1)))

    def test_flecha_para_e_causa_dano_uma_vez_por_trajeto(self):
        inimigo = self.inimigo(490, 400)
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(800)
        self.assertEqual(self.jogo.flecha.estado, 'parada')
        self.assertEqual(inimigo.vida, 9)
        self.avancar(400)
        self.assertEqual(inimigo.vida, 9)
        self.assertTrue(self.jogo.flecha.chamar())
        self.avancar(700)
        self.assertEqual(self.jogo.flecha.estado, 'pronta')
        self.assertEqual(inimigo.vida, 8)

    def test_flecha_pode_retornar_antes_de_parar(self):
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(100)
        self.assertTrue(self.jogo.flecha.chamar())
        self.avancar(200)
        self.assertEqual(self.jogo.flecha.estado, 'pronta')

    def test_flecha_para_nas_quatro_paredes(self):
        for direcao in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            with self.subTest(direcao=direcao):
                self.jogo.flecha.reiniciar()
                self.jogo.flecha.disparar(self.jogador, direcao)
                self.avancar(800)
                self.assertEqual(self.jogo.flecha.estado, 'parada')
                self.assertTrue(self.jogo.cenario.limites.collidepoint(self.jogo.flecha.posicao))

    def test_flecha_nao_atravessa_alvo_sem_acertar_em_passo_longo(self):
        inimigo = self.inimigo(390, 400)
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.jogo.flecha.atualizar(400, self.jogador, self.jogo.inimigos, self.jogo.cenario.limites)
        self.assertEqual(inimigo.vida, 9)

    def test_flecha_retorna_ao_jogador_em_movimento(self):
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(500)
        self.posicionar(500, 550)
        self.jogo.flecha.chamar()
        self.avancar(600)
        self.assertEqual(self.jogo.flecha.estado, 'pronta')

    def test_tiro_triplo_causa_dano_e_desaparece_ao_parar(self):
        self.jogador.inventario.adquirir('triplo')
        inimigo = self.inimigo(470, 400)
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(400)
        self.assertEqual(inimigo.vida, 7)
        self.assertTrue(self.jogo.flecha.tripla)
        self.avancar(400)
        self.assertFalse(self.jogo.flecha.tripla)

    def test_melhorias_de_alcance_velocidade_e_direcao(self):
        self.jogador.inventario.adquirir('distante')
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(800)
        self.assertEqual(self.jogo.flecha.estado, 'voando')
        self.assertGreater(self.jogo.flecha.distancia, 380)
        self.jogo.flecha.reiniciar()
        self.jogador.inventario.adquirir('veloz')
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(100)
        self.assertAlmostEqual(self.jogo.flecha.distancia, 81)
        self.jogo.flecha.reiniciar()
        self.jogador.inventario.adquirir('mental')
        self.inimigo(440, 460)
        self.jogo.flecha.disparar(self.jogador, (1, 0))
        self.avancar(100)
        self.assertGreater(self.jogo.flecha.direcao.y, 0)

    def test_espada_tem_cone_e_recarga(self):
        frente = self.inimigo(358, 400)
        costas = self.inimigo(242, 400)
        self.assertTrue(self.jogo.espada.atacar(self.jogador, (1, 0)))
        self.assertFalse(self.jogo.espada.atacar(self.jogador, (1, 0)))
        self.avancar(160)
        self.assertEqual(frente.vida, 8)
        self.assertEqual(costas.vida, 10)
        self.avancar(300)
        self.assertTrue(self.jogo.espada.atacar(self.jogador, (1, 0)))

    def test_espada_alongada_e_fogo(self):
        alvo = self.inimigo(420, 400)
        self.jogo.espada.atacar(self.jogador, (1, 0))
        self.avancar(500)
        self.assertEqual(alvo.vida, 10)
        self.jogador.inventario.adquirir('espada_longa')
        self.jogador.inventario.adquirir('elemental')
        self.jogo.espada.atacar(self.jogador, (1, 0))
        self.avancar(200)
        self.assertEqual(alvo.vida, 8)
        self.avancar(3000)
        self.assertEqual(alvo.vida, 5)

    def test_dano_tem_intervalo_de_invulnerabilidade(self):
        self.assertTrue(self.jogador.sofrer_dano())
        self.assertFalse(self.jogador.sofrer_dano())
        self.assertEqual(self.jogador.vida, 2)
        self.avancar(1200)
        self.assertTrue(self.jogador.sofrer_dano())
        self.assertEqual(self.jogador.vida, 1)

    def test_golpes_elementais_renovam_duracao_sem_cancelar_dano_periodico(self):
        alvo = self.inimigo(600, 400)
        alvo.receber_dano(1, elemental=True)
        alvo.atualizar(500, self.jogador, self.jogo.cenario.limites, self.jogo.projeteis)
        alvo.receber_dano(1, elemental=True)
        alvo.atualizar(500, self.jogador, self.jogo.cenario.limites, self.jogo.projeteis)
        self.assertEqual(alvo.vida, 7)
        self.assertEqual(alvo.queimando, 2500)

    def test_escudo_absorve_um_golpe_inteiro(self):
        Coletavel('escudo', (300,400), self.recursos).coletar(self.jogador)
        self.jogador.sofrer_dano(2)
        self.assertEqual(self.jogador.vida, 3)
        self.assertEqual(self.jogador.escudo, 0)
        self.jogador.recarregar_escudo()
        self.assertEqual(self.jogador.escudo, 1)

    def test_vida_extra_funciona_apenas_uma_vez(self):
        self.jogador.inventario.adquirir('vida_extra')
        self.jogador.sofrer_dano(5)
        self.assertEqual(self.jogador.vida, 1)
        self.assertTrue(self.jogador.inventario.revive_usado)
        self.assertFalse(self.jogador.inventario.adquirir('vida_extra'))
        self.jogador.invulneravel = 0
        self.jogador.sofrer_dano(1)
        self.assertEqual(self.jogador.vida, 0)

    def test_coracao_nao_e_desperdicado_com_vida_cheia(self):
        coracao = Coletavel('coracao', (300,400), self.recursos)
        self.assertFalse(coracao.coletar(self.jogador))
        self.jogador.vida = 2
        self.assertTrue(coracao.coletar(self.jogador))
        self.assertEqual(self.jogador.vida, 3)

    def test_chances_dos_itens_e_ausencia_de_duplicatas(self):
        for codigo, chance in Inventario.CHANCES:
            with self.subTest(item=codigo):
                inventario = Inventario()
                self.assertIn(codigo, inventario.sortear_recompensas(SorteioFixo(chance - .001)))
                self.assertNotIn(codigo, inventario.sortear_recompensas(SorteioFixo(chance)))
                inventario.adquirir(codigo)
                self.assertNotIn(codigo, inventario.sortear_recompensas(SorteioFixo(0)))

    def test_drop_de_coracao_tem_10_porcento_e_pontos_nao_duplicam(self):
        self.jogo.rng = SorteioFixo(.099)
        alvo = self.inimigo(500, 400)
        alvo.receber_dano(99)
        self.jogo._registrar_mortes()
        pontos = self.jogo.pontos
        self.jogo._registrar_mortes()
        self.assertEqual(self.jogo.pontos, pontos)
        self.assertEqual(len(self.jogo.coletaveis), 1)
        self.jogo.rng = SorteioFixo(.10)
        self.inimigo(600, 400).receber_dano(99)
        self.jogo._registrar_mortes()
        self.assertEqual(len(self.jogo.coletaveis), 1)

    def test_transicao_chama_troca_uma_vez(self):
        chamadas = []
        transicao = Transicao((1024,768), 'Teste', lambda: chamadas.append(True))
        for _ in range(40):
            transicao.atualizar(50)
        self.assertEqual(chamadas, [True])
        self.assertTrue(transicao.finalizada)

    def test_passagem_cura_um_e_recarrega_escudo_ao_limpar(self):
        self.jogador.inventario.adquirir('escudo')
        self.jogador.vida = 1
        self.jogo.sala.concluida = True
        self.jogo.atualizar(20)
        self.assertEqual(self.jogador.escudo, 1)
        self.assertEqual(self.jogo.salas_concluidas, 1)
        self.posicionar(*self.jogo.cenario.portal_saida)
        self.jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e))
        self.avancar(1600)
        self.assertEqual(self.jogo.sala.numero, 2)
        self.assertEqual(self.jogador.vida, 2)
        self.assertEqual(self.jogo.flecha.estado, 'pronta')

    def test_nao_avanca_antes_de_limpar_ou_longe_do_portal(self):
        evento = pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e)
        self.posicionar(*self.jogo.cenario.portal_saida)
        self.jogo.tratar_evento(evento)
        self.assertIsNone(self.jogo.transicao)
        self.jogo.sala.concluida = True
        self.posicionar(300,500)
        self.jogo.tratar_evento(evento)
        self.assertIsNone(self.jogo.transicao)

    def test_pausa_congela_partida_e_bloqueia_ataques(self):
        self.jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.jogo.atualizar(5000)
        self.jogo.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=3,pos=(800,400)))
        self.assertEqual(self.jogo.tempo, 0)
        self.assertEqual(self.jogo.flecha.estado, 'pronta')
        self.assertEqual(self.jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_q)), 'menu')

    def test_morte_espera_animacao_antes_da_derrota(self):
        self.jogador.sofrer_dano(3)
        self.assertIsNone(self.jogo.atualizar(240))
        self.assertEqual(self.jogo.atualizar(240), 'derrota')

    def test_movimento_independe_da_taxa_de_quadros(self):
        teclas = defaultdict(bool, {pygame.K_d: True})
        for _ in range(60):
            self.jogador.atualizar(1000/60, teclas, self.jogo.cenario.limites)
        distancia_60 = self.jogador.posicao.x - 300
        self.posicionar(300,400)
        for _ in range(30):
            self.jogador.atualizar(1000/30, teclas, self.jogo.cenario.limites)
        self.assertAlmostEqual(self.jogador.posicao.x - 300, distancia_60)
        self.assertAlmostEqual(distancia_60, 235)

    def test_diagonal_nao_e_mais_rapida(self):
        teclas = defaultdict(bool, {pygame.K_d: True, pygame.K_s: True})
        self.jogador.atualizar(100, teclas, self.jogo.cenario.limites)
        self.assertAlmostEqual(self.jogador.posicao.distance_to((300,400)), 23.5)

    def test_variedades_e_dificuldade_progressiva(self):
        inicial = Alien((500,400),1,self.recursos)
        avancado = Alien((500,400),5,self.recursos)
        self.assertGreater(avancado.vida, inicial.vida)
        self.assertGreater(avancado.velocidade, inicial.velocidade)
        self.assertEqual(AlienBruto((500,400),4,self.recursos).dano, 2)
        sentinela = AlienAtirador((600,400),2,self.recursos)
        for _ in range(100):
            sentinela.atualizar(20,self.jogador,self.jogo.cenario.limites,self.jogo.projeteis)
        self.assertGreater(len(self.jogo.projeteis),0)
        cacador = AlienCorredor((600,400),3,self.recursos)
        for _ in range(90):
            cacador.atualizar(20,self.jogador,self.jogo.cenario.limites,self.jogo.projeteis)
        self.assertGreater(cacador.aviso,0)

    def test_chefe_muda_fase_e_padrao_de_ataque(self):
        chefe = Chefe((600,300),6,self.recursos)
        for _ in range(81):
            chefe.atualizar(20,self.jogador,self.jogo.cenario.limites,self.jogo.projeteis)
        self.assertEqual(len(self.jogo.projeteis),8)
        self.jogo.projeteis.empty()
        chefe.receber_dano(27)
        chefe.recarga = 20
        chefe.atualizar(20,self.jogador,self.jogo.cenario.limites,self.jogo.projeteis)
        self.assertEqual(chefe.fase,2)
        self.assertEqual(len(self.jogo.projeteis),15)

    def test_projetil_alien_acerta_segmento_e_sai_da_sala(self):
        tiro = ProjetilAlien((200,400),(1,0),400)
        self.jogo.projeteis.add(tiro)
        tiro.atualizar(500,self.jogo.cenario.limites)
        self.assertTrue(tiro.atingiu(self.jogador))
        tiro.atualizar(5000,self.jogo.cenario.limites)
        self.assertNotIn(tiro,self.jogo.projeteis)

    def test_campanha_completa_tem_ondas_finitas_e_vitoria(self):
        self.jogo.sala.espera = 0
        self.jogador.invulneravel = 1_000_000
        surgidos = set()
        tipos = set()
        for _ in range(6000):
            for inimigo in self.jogo.inimigos:
                surgidos.add(inimigo)
                tipos.add(type(inimigo))
                inimigo.receber_dano(999)
            acao = self.jogo.atualizar(50)
            if acao == 'vitoria':
                break
            if self.jogo.sala.concluida and self.jogo.sala.numero < TOTAL_SALAS and not self.jogo.transicao:
                self.posicionar(*self.jogo.cenario.portal_saida)
                self.jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e))
        else:
            self.fail('A campanha não terminou.')
        self.assertEqual(self.jogo.salas_concluidas,6)
        self.assertEqual(len(surgidos),51)
        self.assertEqual(tipos,{Alien,AlienAtirador,AlienCorredor,AlienBruto,Chefe})
        self.assertGreater(self.jogo.pontos,1000)

    def test_reinicio_limpa_itens_e_resultados_usam_tela_correta(self):
        with patch('main.RecursosSprites',return_value=self.recursos), patch('main.Audio',return_value=Audio(False)):
            app = Arrowism()
        self.assertFalse(app.tela.get_flags() & pygame.FULLSCREEN)
        app.tratar_acao('jogar')
        app.tela_atual.jogador.inventario.adquirir('triplo')
        app.tela_atual.pontos = 120
        app.tratar_acao('derrota')
        self.assertIsInstance(app.tela_atual,TelaDerrota)
        self.assertEqual(app.tela_atual.pontos,120)
        app.tratar_acao('jogar')
        self.assertFalse(app.tela_atual.jogador.inventario.adquiridos)
        self.assertEqual(app.tela_atual.pontos,0)
        app.tela_atual.salas_concluidas = 6
        app.tratar_acao('vitoria')
        self.assertIsInstance(app.tela_atual,TelaVitoria)
        app.tratar_acao('menu')
        self.assertIsInstance(app.tela_atual,MenuInicial)
        app.tratar_acao('sair')
        self.assertFalse(app.rodando)

    def test_renderiza_todas_as_telas_e_todos_os_itens(self):
        for codigo in ITENS:
            self.jogador.inventario.adquirir(codigo)
        self.jogo.inimigos.add(Chefe((550,300),6,self.recursos))
        self.jogo.coletaveis.append(Coletavel('triplo',(450,450),self.recursos))
        self.jogo.desenhar(self.tela)
        self.jogo.pausado = True
        self.jogo.desenhar(self.tela)
        MenuInicial((1024,768),self.recursos).desenhar(self.tela)
        TelaDerrota(100,(1024,768),3).desenhar(self.tela)
        TelaVitoria(1000,(1024,768),6).desenhar(self.tela)
        self.assertEqual(self.tela.get_size(),(1024,768))

    def test_audio_original_e_modo_sem_dispositivo(self):
        silencioso = Audio(False)
        silencioso.ambiente('calma')
        silencioso.tocar('flecha')
        silencioso.alternar()
        audio = Audio()
        self.assertTrue(audio.disponivel)
        for contexto in ('calma','combate','chefe'):
            audio.ambiente(contexto)
            som = audio.musicas[contexto]
            self.assertGreater(som.get_length(),5)
            self.assertTrue(any(som.get_raw()))
        audio.alternar()
        self.assertEqual(audio.canal.get_volume(),0)
        audio.alternar()
        self.assertGreater(audio.canal.get_volume(),0)
        pygame.mixer.stop()

    def test_loop_real_processa_foco_reinicio_derrota_menu_e_saida(self):
        with patch('main.RecursosSprites', return_value=self.recursos), patch('main.Audio', return_value=Audio(False)):
            app = Arrowism()
        etapas = []
        partidas = []

        def eventos():
            etapa = len(etapas)
            etapas.append(etapa)
            if etapa == 0:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
            if etapa == 1:
                partidas.append(app.tela_atual)
                return [pygame.event.Event(pygame.WINDOWFOCUSLOST)]
            if etapa == 2:
                self.assertTrue(app.tela_atual.pausado)
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)]
            if etapa == 3:
                self.assertIsNot(app.tela_atual, partidas[0])
                app.tela_atual.transicao = None
                app.tela_atual.jogador.vida = 0
                app.tela_atual.jogador.atualizar(480, defaultdict(bool), app.tela_atual.cenario.limites)
                return []
            if etapa == 4:
                self.assertIsInstance(app.tela_atual, TelaDerrota)
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
            if etapa == 5:
                self.assertIsInstance(app.tela_atual, MenuInicial)
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
            self.fail('O loop não encerrou.')

        try:
            with patch('pygame.event.get', side_effect=eventos):
                app.executar()
            self.assertFalse(pygame.get_init())
            self.assertEqual(len(etapas), 6)
        finally:
            pygame.init()
            type(self).tela = pygame.display.set_mode((1024, 768))


if __name__ == '__main__':
    unittest.main()
