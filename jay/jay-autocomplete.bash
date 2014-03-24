_jay() {
    # this script should be placed in /etc/bash_completion.d/
    # COMPWORDS is an array that contains every param
    # COMP_CWORD is the position the cursor is currently at
    COMPREPLY=(`jay --autocomplete ${COMP_CWORD} ${COMP_WORDS[@]}`)
    return $?
}

complete -F _jay jay
complete -F _jay j
