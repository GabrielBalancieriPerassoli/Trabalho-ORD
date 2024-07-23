Nome: Gabriel Balancieri Perassoli RA: 135854

O trabalho consiste na construção de um programa, cujo, o intuito é fazer um CRUD no arquivo dados.dat. O arquivo dados.dat possui informações sobre jogos online. Os dados dos jogos estão armazenados em registros de tamanho variável. O arquivo possui um cabeçalho de 4 bytes e os campos de tamanho dos registros têm 2 bytes. Cada jogo possui os seguintes campos

Arquivo (dados.dat):

IDENTIFICADOR do jogo (utilizado como chave primária);
TÍTULO;
ANO;
GÊNERO;
PRODUTORA;
PLATAFORMA.
Além disso temos que o programa não terá interface com o usuário e executará as operações na sequência em que estiverem especificadas no arquivo de operações. Dado que iremos executar pela linha de comando usando:

$ python funcoes.py -e arquivo_operacoes.txt

Arquivo (arquivo_operacoes.txt):

b 22
i 147|Resident Evil 2|1998|Survival horror|Capcom|PlayStation|
r 99
r 230
i 181|Pac-Man|1980|Maze|Namco|Arcade|
i 144|The Sims|2000|Life simulation|Electronic Arts|PC|

Teremos também um arquivo chamado funcoes.py, que tem o intuito de executar todas as operacoes do arquivo_operacoes.txt identificando os registros e as operações realizadas, as funcionalidades principais que o funcoes.py tem:

• Busca de um jogo pela CHAVE; • Inserção de um novo jogo; • Reinserir a sobra na LED após a inserção; • Remoção de um jogo; • Imprimir a LED;