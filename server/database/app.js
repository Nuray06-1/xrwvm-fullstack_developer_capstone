const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const Reviews = require('./review');
const Dealerships = require('./dealership');
const app = express();
app.disable('x-powered-by');
app.use(express.json({limit:'32kb'}));
const wrap = fn => (req,res,next) => Promise.resolve(fn(req,res,next)).catch(next);
app.get('/', (req,res)=>res.json({service:'Dealerships and reviews API',status:'ready'}));
app.get('/fetchReviews', wrap(async(req,res)=>res.json(await Reviews.find().select('-_id -__v'))));
app.get('/fetchReviews/dealer/:id',wrap(async(req,res)=>res.json(await Reviews.find({dealership:Number(req.params.id)}).select('-_id -__v'))));
app.get('/fetchDealers',wrap(async(req,res)=>res.json(await Dealerships.find().select('-_id -__v'))));
app.get('/fetchDealers/:state',wrap(async(req,res)=>res.json(await Dealerships.find({state:req.params.state}).select('-_id -__v'))));
app.get('/fetchDealer/:id',wrap(async(req,res)=>{
 const dealer=await Dealerships.findOne({id:Number(req.params.id)}).select('-_id -__v');
 if(!dealer)return res.status(404).json({error:'Dealer not found'});
 res.json(dealer);
}));
const Counter=mongoose.model('Counter',new mongoose.Schema({_id:String,seq:Number}));
app.post('/insert_review',wrap(async(req,res)=>{
 const data=req.body;
 if(typeof data.review!=='string'||data.review.trim().length<3||data.review.length>4000||!Number.isInteger(data.dealership))return res.status(400).json({error:'Invalid review'});
 if(!await Dealerships.exists({id:data.dealership}))return res.status(404).json({error:'Dealer not found'});
 const counter=await Counter.findByIdAndUpdate('reviews',{$inc:{seq:1}},{new:true});
 const fields=['name','dealership','review','purchase','purchase_date','car_make','car_model','car_year'];
 const row=Object.fromEntries(fields.map(k=>[k,data[k]]));
 const result=await Reviews.create({...row,id:counter.seq});res.status(201).json(result);
}));
app.use((error,req,res,next)=>{console.error(error.message);res.status(error.name==='ValidationError'||error.name==='CastError'?400:500).json({error:'Unable to process request'});});
async function start(){
 await mongoose.connect(process.env.MONGO_URL||'mongodb://127.0.0.1:27017/dealershipsDB');
 for(const [Model,file,key] of [[Dealerships,'dealerships.json','dealerships'],[Reviews,'reviews.json','reviews']]){
  if(await Model.countDocuments()===0)await Model.insertMany(JSON.parse(fs.readFileSync(path.join(__dirname,'data',file),'utf8'))[key]);
 }
 const last=await Reviews.findOne().sort({id:-1});
 await Counter.updateOne({_id:'reviews'},{$max:{seq:last?last.id:0}},{upsert:true});
 app.listen(process.env.PORT||3030,'0.0.0.0',()=>console.log('Dealership API listening on port '+(process.env.PORT||3030)));
}
start().catch(e=>{console.error(e.message);process.exit(1)});
