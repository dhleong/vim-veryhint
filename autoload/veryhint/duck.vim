" Author: Daniel Leong
"
"   In a separate file for faster loading when unneeded

function! veryhint#duck#Duck()
    if !exists("b:_veryhint_init")
        " nothing to duck
        return
    endif

    py VeryHint.forBuffer(vim.current.buffer).duck()
endfunction


function! veryhint#duck#Unduck()
    if !exists("b:_veryhint_init")
        " nothing to unduck
        return
    endif

    py VeryHint.forBuffer(vim.current.buffer).unduck()
endfunction
