" Author: Daniel Leong
"

if !has('python') && !has('python3')
    echo 'veryhint requires python support'
    finish
endif

let s:cwdir = expand("<sfile>:p:h")
let s:script = s:cwdir . '/veryhint.py'
py "import vim"
if has('python')
  execute 'pyfile ' . fnameescape(s:script)
elseif has('python3')
  execute 'py3file ' . fnameescape(s:script)
endif

function! veryhint#Init()
    " NB: per docs, during BufWipeout, the "current buffer"
    "  may be different, so let's ensure we pass the right buffer number
    let bufNo = bufnr('%')
    augroup veryhint
        autocmd!
        autocmd InsertLeave <buffer> call veryhint#HideHints()
        " TODO how is jedi able to handle ctrl-c to hide hints?
        exe 'autocmd BufWipeout <buffer> py VeryHint.cleanup(' . bufNo . ')'
    augroup END

    " TODO this is where we load syntax
endfunction

function! veryhint#ShowHints(hints)
    if !exists("b:_veryhint_init")
        call veryhint#Init()
        let b:_veryhint_init = 1
    endif

python << PYEOF
hints = vim.bindeval("a:hints")
cursor = vim.current.window.cursor
VeryHint.forBuffer(vim.current.buffer).showHints(hints, cursor)
PYEOF

    return ''
endfunction

function! veryhint#HideHints()
    py VeryHint.forBuffer(vim.current.buffer).hideHints()

    " TODO remove the hint-creating history somehow?

    return ''
endfunction


" vim:ft=vim:fdm=marker
