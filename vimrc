syntax on
set ruler
set tabstop=4
set shiftwidth=4
set expandtab
set hlsearch
set wildmenu
set wildignore=*.pyc,*.pyo,*.class
set autoread
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
xnoremap p pgvy
noremap <F1> :w<Return>
noremap <F2> :wq<Return>
noremap ` :q<Return>
inoremap <F1> <Esc>:w<Return>
inoremap <F2> <Esc>:wq<Return>
noremap <F7> :set number!<Return> 
inoremap <F7> :set number!<Return> 
noremap <Tab> i<Space><Space><Space><Space><Esc>l
noremap <F3> <C-w><C-w>
inoremap <F3> <Esc><C-w><C-w>i
noremap ! *
noremap <F10> `a
noremap <F9> ma
noremap <F5> :e ~/index<Return>/
inoremap <F5> :e ~/index<Return>/
noremap <F6> gf
noremap <Space> i<Space><Esc><Right>
noremap Q viwy
noremap A a
noremap Y Vy
noremap <C-n> :tabnew<Return>
noremap <C-o> :tabnew<Return>:e .<Return>
vnoremap // y/<C-R>"<Return>
noremap <F11> :tabnew<Return>:CtrlP<Return> 
noremap <F12> `
noremap \ :e ~/index<Return>/
noremap c C<Esc>

set runtimepath^=~/.vim/bundle/ctrlp.vim
let g:ctrlp_regexp = 1
let g:ctrlp_by_filename = 1
"set incsearch
"set ignorecase
