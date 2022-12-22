module.exports = {
  devServer: {
    proxy: 'http://127.0.0.1:5000'
  },
  chainWebpack: (config) => {
    config.module
      .rule('vue')
      .use('vue-loader')
      .tap((args) => {
        args.compilerOptions.whitespace = 'preserve'
      })
  }
}
