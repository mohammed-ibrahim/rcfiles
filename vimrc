syntax on
set ruler
set tabstop=4
set shiftwidth=4
set expandtab
set hlsearch
set wildmenu
set wildignore=*.pyc,*.pyo,*.class
set autoread
set nocompatible
set complete-=i
"syntax enable
"filetype plugin on
"set path+=**
"filetype plugin indent on

au BufRead,BufNewFile *.scala         setfiletype scala
au BufRead,BufNewFile *.scala         set shiftwidth=2
au FileType scala setl sw=2 sts=2 et

noremap - dd
noremap ; O<Esc>
noremap ' o<Esc>
noremap = $
noremap { <C-b>
noremap } <C-f>
noremap [ gT
noremap ] gt
noremap a A
noremap l G
noremap j 15k
noremap k 15j
noremap K i<Return><Esc>
noremap q viw

noremap <F1> :w<Return>
noremap <F2> :wq<Return>
noremap <F3> <C-w><C-w>
noremap <F4> /\C<Left><Left>
noremap <F5> :e ~/index<Return>/
noremap <F6> gf
noremap <F7> :set number!<Return>
noremap <F9> ma
noremap <F10> `a
noremap <F11> :tabnew<Return>:e ~/index<Return>/
noremap <F12> `

noremap ` :q<Return>
noremap <Tab> i<Space><Space><Space><Space><Esc>l
noremap ! *
noremap @ gf
noremap <Space> i<Space><Esc><Right>
noremap Q viwy
noremap A a
noremap Y Vy
noremap \ :e ~/index<Return>/
noremap c C<Esc>

inoremap <C-o> <C-x><C-n>
inoremap <F1> <Esc>:w<Return>
inoremap <F2> <Esc>:wq<Return>
inoremap <F3> <Esc><C-w><C-w>i
inoremap <F5> :e ~/index<Return>/
inoremap <F7> :set number!<Return>
inoremap <C-e> <Esc>$i

xnoremap p pgvy
cnoremap @ <Return>gf
vnoremap // y/<C-R>"<Return>

set incsearch
set ignorecase
