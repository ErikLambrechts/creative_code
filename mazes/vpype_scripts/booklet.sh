#!/bin/sh

build_page_4_4() {
    vpype \
        eval "files=sorted(glob($4))" \
        eval "cols=4; rows=4" \
        eval "list=$2" \
        layout a4\
        eval "w,h = prop.vp_page_size" \
        grid -o %w/cols% %h/rows% "%cols%" "%rows%" \
            read --no-fail "%files[list[_i]-1] if _i < len(files) else ''%" \
            scaleto -o 0 0 50mm 50mm \
            translate -- -25mm -25mm \
            layout -v center -h center --fit-to-margins 5mm %w/cols%x%h/rows%\
            text -l 2 -s 18 -p 5mm  70mm --align 'left'  "%'' if divmod(list[_i],2)[1]==1 else (list[_i])%" \
            text -l 2 -s 18 -p 45mm 70mm --align 'right' "%'' if divmod(list[_i],2)[1]==0 else (list[_i])%" \
            lmove 1,2 1 \
            layout -v center -h center --fit-to-margins 5mm %w/cols%x%h/rows%\
            rotate "%180 if divmod(_y, 2)[1]  == 0 else 0%" \
        end \
        deduplicate \
        write $3/$1.svg
}

#!/bin/sh

build_page_4_4() {
    vpype \
        eval "files=sorted(glob($4))" \
        eval "cols=4; rows=4" \
        eval "list=$2" \
        layout a4\
        eval "w,h = prop.vp_page_size" \
        grid -o %w/cols% %h/rows% "%cols%" "%rows%" \
            read --no-fail "%files[list[_i]-1] if _i < len(files) else ''%" \
            deduplicate \
            scaleto -o 0 0 50mm 50mm \
            translate -- -25mm -25mm \
            eval "layer=(2 if divmod(list[_i],2)[1]==1 else 1)+(2 if divmod(_y,2)[1]==1 else 0)" \
            eval "align='left' if divmod(list[_i],2)[1]==1 else 'right'" \
            text -l %layer+4% -s 18 --align {align} "%list[_i]%" \
            layout -v center -h center --fit-to-margins 5mm %w/cols%x%h/rows% \
            rotate "%180 if divmod(_y, 2)[1]  == 0 else 0%" \
        end \
        translate -l 5 5mm 70mm \
        translate -l 6 45mm 70mm\
        write $3/$1.svg
}
build_page_4_4 front "5,28,29,4,12,21,20,13,9,24,17,16,8,23,32,1" ${1:-./} ${2:-"'../output/grid/*.svg'"}
build_page_4_4 back "3,30,27,6,14,19,22,11,15,18,23,10,2,31,26,7" ${1:-./} ${2:-"'../output/grid/*.svg'"}

to_gcode() {
    echo $1.svg
    vpype \
        --config gwrite.toml \
        read "$1.svg" linesort \
        linemerge \
        gwrite -p plotbot $1.gcode
} 

to_gcode ${1:-./}/front
to_gcode ${1:-./}/back