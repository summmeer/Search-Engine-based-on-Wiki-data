import axios from 'axios'

axios.default.timeout = 5000
axios.defaults.headers.post['Content-Type'] = 'application/json'

const instance = axios.create();
instance.defaults.headers.post['Content-Type'] = 'application/json';

axios.interceptors.request.use = instance.interceptors.request.use;
const base_url = "http://localhost:5000";
export default {
    getContentById(data) {
        console.log(base_url+"/getContentById?id="+data.id)
        return instance.get(base_url+"/getContentById?id="+data.id)
    },
    search(data) {
        return instance.post(base_url+"/search", data)
    },
    getPage(data) {
        return instance.post(base_url+"/getPageByIds", data)
    }
}