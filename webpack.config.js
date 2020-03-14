module.exports = {
  entry: ["./src/react/app.js"],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ["babel-loader"]
      },
      {
        test: /\.less$/,
        use: [
          { loader: "style-loader" },
          { loader: "css-loader" },
          { loader: "less-loader" }
        ]
      }
    ]
  },
  output: {
    path: __dirname + "/dist/static/js",
    filename: "bundle.js"
  }
};
