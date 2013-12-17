function j {
    output="$(jay ${@})"
    if [ -d "${output}" ]; then
        echo -e "\\033[31m${output}\\033[0m"
        cd "${output}"
    else
        echo ${output}
        false
    fi
}
