<template>
  <div class="hello">
    <h1>{{ title }}</h1>
    original link: <a v-bind:href="url">{{ url }}</a>
    <p align="left" class="text" v-html="content"></p>

  </div>
</template>


<script>
import api from '../axios'

export default {
  name: 'HelloWorld',
  data () {
    return {
      title: "",
      content: "",
      url: ""
    }
  },
  mounted () {
    this.searchById();
  },
  methods: {
    searchById() {
      let data = {
        id: this.$route.params.id
      }
      console.log(this.input)
      let that = this
      api.getContentById(data).then((res) => {
          console.log(res.data)
          that.title = res.data[0]['title']
          let text = res.data[0]['content']
          that.url = res.data[0]['url']
          let i = text.indexOf('\n')
          text = text.slice(i+2).replace(/\n/g, '<br>')
          text = text.replace(/<a href=\"/g, '<a href=\"https://en.wikipedia.org/wiki/')
          that.content = text
      }, (err) => {
      })
    }
  }
}
</script>