cp customrc ~/.customrc
cp vimrc ~/.vimrc
cd ~/.vim
git clone https://github.com/kien/ctrlp.vim.git bundle/ctrlp.vim
echo ". ~/.customrc" >> ~/.bashrc
