import sys
import io

ListaLED = []

def leia_reg(arq) -> tuple[str, int]:

    try:

        tam_bytes = arq.read(2)  # Leia 2 bytes

        if len(tam_bytes) < 2: # Se for menor que 2 bytes retorna vazio

            return '', 0
        
        tam = int.from_bytes(tam_bytes, byteorder='big') # Converte para decimal os bytes

        if tam > 0: # Se o tamanho for maior que 0

            buffer = arq.read(tam) # Faça um read para o tam e decodifique para string

            return buffer.decode('utf-8', errors='replace'), tam
        
    except OSError as e:

        print(f'Erro leia_reg: {e}')

    return '', 0

def busca(chave, imprimir=True) -> int:

    try:

        with open("dados.dat", 'rb') as arq:

            arq.read(4)  # Pula o cabeçalho de 4 bytes
            achou = False # Inicia como False
            buffer, tam = leia_reg(arq) # Leia o registro
            offset = 4

            if imprimir:
                print(f'Busca pelo registro de "{chave}"')

            while buffer and not achou: # Enquanto tem algo no buffer e não achou

                key = buffer.split('|')[0] # Pega o primeiro campo do registro

                if chave == key: # Se a chave procurada for igual a key do registro

                    achou = True
                    if imprimir:
                        print(f"{buffer} ({tam} bytes)")

                else: # Se não for igual, faça o processo novamente

                    offset = offset + tam + 2
                    buffer, tam = leia_reg(arq)
                    
            if not achou: # Se ele saiu do while indica que o arquivo acabou, logo ele não achou a chave no arquivo

                if imprimir:
                    print(f'Jogo com identificador {chave} não encontrado.')
                return -1
            
            if imprimir:
                print()

            return offset

    except OSError as e:
        print(f"Erro ao abrir 'dados.dat': {e}")

def imprimeLED(imprimir=True):

    try:

        with open("dados.dat", 'r+b') as arq:

            arq.seek(0)  # Posiciona no começo do arquivo
            ledCabecalho = arq.read(4)  # Lê os 4 bytes (cabeçalho)
            led = int.from_bytes(ledCabecalho, byteorder='big', signed=True)  # Converte os bytes lidos do cabeçalho para um inteiro

            if led == -1:  # Verifica se a LED está vazia
                if imprimir:
                    print()
                    print("LED está vazia.")
                    print()
                return
            
            cont = 0
 
            print()
            print("LED -> ", end='')

            while led != -1:  # Se LED não está vazia, percorra ela

                arq.seek(led)  # Posiciona o ponteiro para o offset atual da LED
                espaco = int.from_bytes(arq.read(2), byteorder='big')  # Lê os próximos 2 bytes para obter o tamanho do espaço
                arq.read(1)  # Pula o "*"
                proxOffset = int.from_bytes(arq.read(4), byteorder='big', signed=True)  # Lê os próximos 4 bytes para obter o próximo offset

                if imprimir:
                    print(f"[offset: {led}, tam: {espaco}] -> ", end='')

                led = proxOffset  # Atualiza a LED para o próximo offset
            
                cont += 1

            if imprimir:
                print("[offset: -1]")
                print(f"Total: {cont} espaços disponíveis", end='')
                print("\n")

    except IOError as e:
        print(f"Erro ao abrir o arquivo: {e}")

def reinserirSobraLED(arq, sobra, offsetSobra):
    arq.seek(0)
    ledCabecalho = arq.read(4)
    led = int.from_bytes(ledCabecalho, byteorder='big', signed=True)

    offsetAnterior = -1
    offsetAtual = led
    inserido = False

    while offsetAtual != -1 and not inserido:
        arq.seek(offsetAtual)
        espacoAtual = int.from_bytes(arq.read(2), byteorder='big')
        arq.read(1)  # Pula o "*"
        proxOffset = int.from_bytes(arq.read(4), byteorder='big', signed=True)

        if sobra > espacoAtual:
            # Encontrou a posição correta para inserir a sobra
            if offsetAnterior == -1:
                # Atualiza o cabeçalho da LED
                arq.seek(0)
                arq.write(offsetSobra.to_bytes(4, byteorder='big', signed=True))
            else:
                # Atualiza o ponteiro do espaço anterior para apontar para a sobra
                arq.seek(offsetAnterior + 3)
                arq.write(offsetSobra.to_bytes(4, byteorder='big', signed=True))

            # Configura a sobra para apontar para o espaço atual
            arq.seek(offsetSobra)
            arq.write(sobra.to_bytes(2, byteorder='big'))  # Escreve o tamanho da sobra
            arq.write(b"*")  # Escreve o marcador "*"
            arq.write(proxOffset.to_bytes(4, byteorder='big', signed=True))  # Encadeia com o próximo espaço
            inserido = True
        else:
            offsetAnterior = offsetAtual
            offsetAtual = proxOffset

    if not inserido:
        # Se não encontrou uma posição, insere no final
        if offsetAnterior == -1:
            # Se a LED estava vazia, atualiza o cabeçalho
            arq.seek(0)
            arq.write(offsetSobra.to_bytes(4, byteorder='big', signed=True))
        else:
            # Atualiza o ponteiro do último espaço para apontar para a sobra
            arq.seek(offsetAnterior + 3)
            arq.write(offsetSobra.to_bytes(4, byteorder='big', signed=True))

        # Configura a sobra para ser o último elemento
        arq.seek(offsetSobra)
        arq.write(sobra.to_bytes(2, byteorder='big'))  # Escreve o tamanho da sobra
        arq.write(b"*")  # Escreve o marcador "*"
        arq.write((-1).to_bytes(4, byteorder='big', signed=True))  # Indica que não há próximo

def insere(registro):
    try:
        chave = registro.split('|')[0]

        with open("dados.dat", 'r+b') as arq:
            arq.seek(0)
            ledCabecalho = arq.read(4)
            led = int.from_bytes(ledCabecalho, byteorder='big', signed=True)

            print(f'Inserção do registro de chave "{chave}" ({len(registro)} bytes)')

            tamRegistro = len(registro)  # Inclui os bytes do tamanho do registro

            encontrado = False
            offsetAnterior = -1
            offsetAtual = led
            offsetInsercao = None
            espaco = None  # Garantindo que espaco seja definido

            while offsetAtual != -1 and not encontrado:
                arq.seek(offsetAtual)
                espaco = int.from_bytes(arq.read(2), byteorder='big')
                arq.read(1)  # Pula o "*"
                proxOffset = int.from_bytes(arq.read(4), byteorder='big', signed=True)

                if espaco >= tamRegistro:
                    encontrado = True
                    sobra = espaco - tamRegistro - 2

                    # Atualiza a cabeça da LED para o próximo espaço livre
                    if offsetAnterior == -1:  # Se o espaço estava na cabeça da LED
                        arq.seek(0)
                        arq.write(proxOffset.to_bytes(4, byteorder='big', signed=True))
                    else:  # Atualiza o encadeamento da LED
                        arq.seek(offsetAnterior + 3)
                        arq.write(proxOffset.to_bytes(4, byteorder='big', signed=True))

                    # Posiciona para escrever o registro
                    arq.seek(offsetAtual)
                    arq.write(tamRegistro.to_bytes(2, byteorder='big'))
                    arq.write(registro.encode('utf-8'))

                    offsetInsercao = offsetAtual + tamRegistro + 2

                else:
                    offsetAnterior = offsetAtual
                    offsetAtual = proxOffset

            if encontrado:
                if sobra > 10:  # Se encontrou espaço e sobra é significativa
                    print(f"Tamanho do espaço reutilizado: {espaco} bytes (Sobra de {sobra} bytes)")
                    print(f"Local: offset = {offsetAtual} ({ledCabecalho})")
                    print()
                    reinserirSobraLED(arq, sobra, offsetInsercao)
                else:  # Se não há sobra significativa
                    print(f"Tamanho do espaço reutilizado: {espaco} bytes")
                    print(f"Local: offset = {offsetAtual} ({ledCabecalho})")
                    print()

            if not encontrado:
                # Se não encontrou espaço, insere no final do arquivo
                arq.seek(0, io.SEEK_END)
                posicao = arq.tell()
                arq.write(tamRegistro.to_bytes(2, byteorder='big'))
                arq.write(registro.encode('utf-8'))
                print(f'Tamanho do espaço utilizado: {tamRegistro} bytes')
                print(f'Local: fim do arquivo (offset = {posicao})')
                print()

    except OSError as e:
        print(f"Erro ao abrir 'dados.dat': {e}")

def remove(chave):

    try:

        offset = busca(chave, imprimir=False)

        if offset == -1:

            print(f'Remoção do registro de chave "{chave}"')
            print('Erro: registro não encontrado!')
            print()
            return  # Se a busca não encontrou o registro, encerra a função

        with open("dados.dat", 'r+b') as arq:  # Abre o arquivo 'dados.dat' no modo de leitura e escrita binária

            arq.seek(0)  # Posiciona no começo do arquivo
            ledCabecalho = arq.read(4)  # Lê os 4 bytes (cabeçalho)
            led = int.from_bytes(ledCabecalho, byteorder='big', signed=True)  # Converte os bytes lidos do cabeçalho para um inteiro

            arq.seek(offset)  # Posiciona o cursor no offset encontrado
            tamBytes = arq.read(2)  # Lê os próximos 2 bytes para obter o tamanho do registro

            if tamBytes:

                tam = int.from_bytes(tamBytes, byteorder='big')  # Converte os 2 bytes, que representa o tamanho do registro
                arq.read(tam)  # Lê o registro para posicionar o cursor após ele

                print(f'Remoção do registro de chave "{chave}"')  # print indicando que a remoção do registro foi iniciada

                arq.seek(offset + 2)  # Posiciona o cursor no início do registro e avança 2 bytes do tamanho
                arq.write(b'*')  # Marca o registro como deletado usando '*'

                novoEspacoTam = tam  # Tamanho do novo espaço liberado é o tamanho do registro removido
                novoEspacoOffset = offset  # Offset do novo espaço liberado é o offset do registro removido

                if led == -1:  # Se a LED estiver vazia, atualiza o cabeçalho com o novo espaço

                    arq.seek(0)  # Posiciona o cursor no início do arquivo (cabeçalho)
                    arq.write((novoEspacoOffset).to_bytes(4, byteorder='big', signed=True))  # Escreve o offset do novo espaço no cabeçalho

                    arq.seek(novoEspacoOffset + 3)  # Posiciona o cursor 2 bytes após para escrever o próximo
                    arq.write((-1).to_bytes(4, byteorder='big', signed=True))  # Escreve -1 no próximo para indicar o fim da lista

                else:  # Se a LED não estiver vazia, percorre a lista para encontrar a posição correta

                    antOffset = -1  # Inicializa o offset anterior como -1 (não há anterior no início)
                    atualOffset = led  # Inicializa o offset atual com o início da LED

                    while atualOffset != -1:  # Se o atual offset for diferente de -1 quer dizer que já foi encadeado coisas lá antes

                        arq.seek(atualOffset)  # Posiciona o cursor no início do espaço atual
                        atualEspacoTam = int.from_bytes(arq.read(2), byteorder='big')  # Lê e converte os 2 bytes para obter o tamanho do espaço atual

                        arq.read(1) # Pula o "*"
                        proxOffset = int.from_bytes(arq.read(4), byteorder='big', signed=True)  # Lê e converte os 4 bytes para obter o próximo offset

                        if novoEspacoTam > atualEspacoTam:  # Se o novo espaço for maior que o espaço atual, interrompe o loop

                            break  # Interrompe o loop se o novo espaço for maior que o espaço atual

                        # Atualiza os offsets para continuar percorrendo a lista
                        antOffset = atualOffset  # Atualiza o offset anterior para o offset atual
                        atualOffset = proxOffset  # Atualiza o offset atual para o próximo offset

                    if antOffset == -1:  # Se o novo espaço deve ser inserido no início da lista

                        arq.seek(0)  # Posiciona o cursor no início do arquivo 
                        arq.write(novoEspacoOffset.to_bytes(4, byteorder='big', signed=True))  # Escreve o offset do novo espaço no cabeçalho

                    else:  # Se o novo espaço deve ser inserido no meio ou no final da lista

                        arq.seek(antOffset + 3)  # Posiciona o cursor 2 bytes após o início do espaço anterior
                        arq.write(novoEspacoOffset.to_bytes(4, byteorder='big', signed=True))  # Escreve o offset do novo espaço no espaço anterior

                    arq.seek(novoEspacoOffset + 3)  # Posiciona o cursor 2 bytes após o início do novo espaço
                    arq.write(atualOffset.to_bytes(4, byteorder='big', signed=True))  # Escreve o offset do espaço atual no novo espaço

                print(f'Registro removido! ({tam} bytes)')
                print(f'Local: offset = {offset}')
                print()

    except OSError as e:
        print(f"Erro ao abrir 'dados.dat': {e}")

def arquivo(nomeArq):

    try:

        with open(nomeArq, "r") as arq:

            linhas = arq.readlines()  # Transforma as linhas em um array
            tamLinha = len(linhas)  # Pega o número de linhas a partir do tamanho do array
            i = 0  # Inicializa o contador

            while i < tamLinha:  # Enquanto o contador for menor que o número de linhas

                linha = linhas[i].strip()  # Remove espaços em branco e quebras de linha no início e no fim

                if linha:  # Verifica se a linha não está vazia
                    
                    operacao = linha[0]  # Pega o primeiro caractere da linha para determinar a operação

                    if len(linha.split()) > 1:  # Verifica se a linha tem partes suficientes para extrair a chave

                        chave = linha.split()[1]  # Pega a chave, que é o segundo elemento após o split
                        chave = chave.split(sep='|')[0] # Pega a chave que está antes do Pipe

                        if operacao == "b":  # Se o char for igual a b, é busca

                            busca(chave)  # Faz a chamada de função passando a chave como parâmetro

                        elif operacao == "r":  # Se o char for igual a r, é remoção

                            remove(chave)

                        elif operacao == "i":  # Se o char for igual a i, seria inserção

                            indiceEspaco = linha.index(' ')
                            registro = linha[indiceEspaco + 1:] # Fatiar a string a partir do índice do primeiro espaço

                            insere(registro)

                        else:

                            print(f"Operação '{operacao}' não reconhecida.")

                    else:

                        print("Linha mal formatada ou faltando chave: ", linha)

                i += 1  # Incrementa o contador para processar a próxima linha

    except OSError as e:
        print(f"Erro ao abrir '{nomeArq}': {e}")

nomeArq = "arquivo_operacoes.txt"

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == '-e': # Executa as operações do arquivo_operacoes.txt
        nomeArq = sys.argv[2]
        arquivo(nomeArq)
    elif len(sys.argv) == 2 and sys.argv[1] == '-p': # Mostra a LED com os espaços disponiveis
        imprimeLED(imprimir=True)
    else:
        print("Uso: python funcoes.py -e arquivo_operacoes.txt") 
        print("Ou: python funcoes.py -p")