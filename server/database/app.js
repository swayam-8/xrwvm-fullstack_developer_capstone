const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const Reviews = require('./review');
const Dealerships = require('./dealership');
const app = express();
app.disable('x-powered-by');
app.use(cors());
app.use(express.json({limit:'32kb'}));
const asyncRoute = fn => (req,res,next) => Promise.resolve(fn(req,res,next)).catch(next);
const asId = value => { const id = Number(value); if (!Number.isSafeInteger(id) || id < 1) { const e = new Error('Invalid dealer ID'); e.status=400; throw e; } return id; };
app.get('/', (req,res)=>res.json({service:'Dealership Express-Mongo API',status:'ready'}));
app.get('/health', (req,res)=>res.status(mongoose.connection.readyState === 1 ? 200 : 503).json({database:mongoose.connection.readyState === 1 ? 'connected':'unavailable'}));
app.get('/fetchReviews', asyncRoute(async(req,res)=>res.json(await Reviews.find().select('-_id -__v').lean())));
app.get('/fetchReviews/dealer/:id',asyncRoute(async(req,res)=>res.json(await Reviews.find({dealership:asId(req.params.id)}).sort({id:-1}).select('-_id -__v').lean())));
app.get('/fetchDealers',asyncRoute(async(req,res)=>res.json(await Dealerships.find().sort({id:1}).select('-_id -__v').lean())));
app.get('/fetchDealers/:state',asyncRoute(async(req,res)=>res.json(await Dealerships.find({state:req.params.state}).sort({id:1}).select('-_id -__v').lean())));
app.get('/fetchDealer/:id',asyncRoute(async(req,res)=>res.json(await Dealerships.find({id:asId(req.params.id)}).select('-_id -__v').lean())));
const counterSchema = new mongoose.Schema({_id:String,seq:Number});
const Counter = mongoose.model('Counter',counterSchema);
app.post('/insert_review',asyncRoute(async(req,res)=>{
 const b=req.body;
 const dealership=asId(b.dealership);
 if (!(await Dealerships.exists({id:dealership}))) return res.status(404).json({message:'Dealer not found'});
 for(const key of ['name','review','purchase_date','car_make','car_model']) if(typeof b[key]!=='string'||!b[key].trim()) return res.status(400).json({message:`Missing ${key}`});
 const year=Number(b.car_year);
 if(!Number.isInteger(year)||year<2015||year>2026) return res.status(400).json({message:'Invalid car year'});
 const count=await Counter.findOneAndUpdate({_id:'review'},{$inc:{seq:1}},{new:true});
 const review=await Reviews.create({id:count.seq,name:b.name,dealership,review:b.review,purchase:Boolean(b.purchase),purchase_date:b.purchase_date,car_make:b.car_make,car_model:b.car_model,car_year:year});
 res.status(201).json(review.toObject());
}));
app.use((error,req,res,next)=>res.status(error.status||500).json({message:error.status?error.message:'Database request failed'}));
async function start(){
 await mongoose.connect(process.env.MONGO_URL||'mongodb://127.0.0.1:27017/dealershipsDB');
 for(const [filename,key,Model] of [['dealerships.json','dealerships',Dealerships],['reviews.json','reviews',Reviews]]){
  const records=JSON.parse(fs.readFileSync(path.join(__dirname,'data',filename)))[key];
  await Model.bulkWrite(records.map(record=>({updateOne:{filter:{id:record.id},update:{$setOnInsert:record},upsert:true}})));
 }
 const latest=await Reviews.findOne().sort({id:-1});
 await Counter.updateOne({_id:'review'},{$max:{seq:latest?latest.id:0}},{upsert:true});
 const port=process.env.PORT||3030;
 return app.listen(port,'0.0.0.0',()=>console.log(`Express-Mongo API running on port ${port}`));
}
if(require.main===module)start().catch(error=>{console.error(error.message);process.exit(1);});
module.exports={app,start};
