#!/bin/sh
# Genera la aplicacion nativa con jpackage (requiere JDK 17+). Ejecutar desde avance_4/jpackage
set -e
rm -rf build salida && mkdir -p build/clases build/entrada salida
javac -d build/clases src/Lanzador.java
jar --create --file build/entrada/lanzador.jar --main-class Lanzador -C build/clases .
# Copia del proyecto que viaja dentro de la aplicacion
mkdir -p build/entrada/proyecto
cp -r ../app.py ../main.py ../requirements.txt ../src ../interfaz ../datos ../resultados build/entrada/proyecto/
jpackage --type "${1:-app-image}" --name DashboardClimatico --app-version 1.0 \
  --vendor "Parra, Carrillo, Leiva" --description "Dashboard de comportamiento climatico integrado" \
  --input build/entrada --main-jar lanzador.jar --main-class Lanzador --dest salida
echo "Listo: salida/"
