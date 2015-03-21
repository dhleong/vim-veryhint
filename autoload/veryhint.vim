" Author: Daniel Leong
"

" SETUP {{{
if !has('python') && !has('python3')
    echo 'veryhint requires python support'
    finish
endif

let s:cwdir = expand("<sfile>:p:h")
let s:script = s:cwdir . '/veryhint.py'
if has('python')
    execute 'pyfile ' . fnameescape(s:script)
elseif has('python3')
    execute 'py3file ' . fnameescape(s:script)
endif

python << PYEOF
import vim
PYEOF

" }}} 

function! veryhint#ShowHints(hints) " {{{
    if !exists("b:_veryhint_init")
        call s:Init()
        let b:_veryhint_init = 1
    endif

    let b:_veryhint_shown = a:hints
    let b:_veryhint_line = line('.')
    let b:_veryhint_col = col('.')

python << PYEOF
hints = vim.bindeval("a:hints")
cursor = vim.current.window.cursor
VeryHint.forBuffer(vim.current.buffer).showHints(hints, cursor)
PYEOF

    return ''
endfunction " }}}

function! veryhint#HideHints() " {{{
    py VeryHint.forBuffer(vim.current.buffer).hideHints()

    if exists('b:_veryhint_shown')
        unlet b:_veryhint_shown
        unlet b:_veryhint_line
        unlet b:_veryhint_col
    endif

    return ''
endfunction " }}}

"
" Private utils
"

function! s:Init() " {{{
    " NB: per docs, during BufWipeout, the "current buffer"
    "  may be different, so let's ensure we pass the right buffer number
    let bufNo = bufnr('%')
    augroup veryhint
        autocmd!
        autocmd InsertLeave <buffer> call veryhint#HideHints()
        autocmd CursorMoved <buffer> call veryhint#HideHints()
        autocmd CursorMovedI <buffer> call <SID>AdjustHints()
        exe 'autocmd BufWipeout <buffer> py VeryHint.cleanup(' . bufNo . ')'
    augroup END

    " TODO this is where we load syntax
endfunction " }}}

function! s:AdjustHints() " {{{
    let line = line('.')
    let col = col('.')

    if !exists('b:_veryhint_line')
        return
    endif

    if line != b:_veryhint_line || col < b:_veryhint_col
        call veryhint#duck#Duck()
    else
        call veryhint#duck#Unduck()
    endif
endfunction " }}}

" vim:ft=vim:fdm=marker
