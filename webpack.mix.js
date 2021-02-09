let mix = require('laravel-mix')

mix.setPublicPath('app/assets/public')
    .css('app/assets/css/swagger-ui.css', 'css/swagger-ui.css')
    .sass('app/assets/scss/error_code.scss', 'css/error_code.css')
    .version()
